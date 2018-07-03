from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views.generic import View
from django.core.paginator import Paginator
from .models import (
    BinaryTree,
    BinaryPointsHistory,
    STATUS_CHOICES,
)
from settings.models import Setting
import json
from .utils import SetPoints


APP_SETTINGS = Setting.objects.first()
TOKEN_NOT_VALID_MESSAGE = 'Не верный API токен'


def is_valid_api_key(api_key):
    """
    Проверка на вилидность API ключа
    :param api_key:
    :return: bool
    """
    my_api_key = APP_SETTINGS.api_secret_key
    if my_api_key == api_key:
        return True
    return False


def get_parameters(request):
    try:
        parameters = json.loads(request, encoding='UTF-8')
    except:
        return False

    return parameters


def bad_request():
    context = {
        'status': False,
        'message': 'Не верный формат запроса',
    }
    return JsonResponse(context)


@method_decorator(csrf_exempt, name='dispatch')
class GetTreeAPIView(View):
    """
    Получение бинарного дерева
    ПАРАМЕТРЫ В BODY (JSON)
    root_node:
        root - вернуть всё дерево
        username - вернуть дерево начиная с указаного пользователя
    """

    def post(self, request, api_key):
        context = {}

        if not is_valid_api_key(api_key):
            context['status'] = False
            context['message'] = TOKEN_NOT_VALID_MESSAGE
            return JsonResponse(context)

        parameters = get_parameters(self.request.body)
        if not parameters:
            return bad_request()

        username = parameters.get('root_node')
        if username:
            try:
                node = BinaryTree.objects.get(user=username)
            except BinaryTree.DoesNotExist:
                context['status'] = False
                context['message'] = 'Пользователя {} не существует'.format(username)
                return JsonResponse(context)
        else:
            return bad_request()

        tree = list()
        nodes = node.get_descendants(include_self=True).filter(level__lte=APP_SETTINGS.tree_deep)

        for i in nodes:
            element = dict()
            element['id'] = i.id
            element['name'] = i.user
            element['parentId'] = i.parent.id if i.parent else None
            element['level'] = i.level
            element['left_node'] = i.left_node if i.left_node else False
            element['right_node'] = i.right_node if i.right_node else False
            element['left_points'] = 'Баллы в левой ноге - {}'.format(i.left_points)
            element['right_points'] = 'Баллы в правой ноге - {}'.format(i.right_points)
            element['status'] = i.status
            element['created'] = i.created

            if node.left_node or node.right_node:
                element['look_tree'] = "<a class='look_tree' href='#{}'><i class='fa fa-3x fa-chevron-down'></i></a>".format(i.user)
            else:
                element['look_tree'] = "<span class='hidden'>1</span>"

            if i.level == APP_SETTINGS.tree_deep:
                element['skip_children'] = True

            tree.append(element)

        context['status'] = True
        context['tree'] = tree

        return JsonResponse(context)


@method_decorator(csrf_exempt, name='dispatch')
class SetUserInBinaryAPIView(View):
    """
    Добавление пользователя в бинарное дерево
    ПАРАМЕТРЫ В BODY (JSON)
    parent:
        username - Логин родителя
    leg:
        left_node - Поставить пользователя в левую ногу
        right_node - Поставить пользователя в правую ногу
    username:
        string - Имя пользователя (уникальное)
    points:
        int - Сумма балов для присвоения по структуре вверх
    """

    def post(self, request, api_key):
        context = {}

        if not is_valid_api_key(api_key):
            context['status'] = False
            context['message'] = TOKEN_NOT_VALID_MESSAGE
            return JsonResponse(context)

        parameters = get_parameters(self.request.body)
        if not parameters:
            return bad_request()

        new_user_name = parameters.get('username')
        points = parameters.get('points')
        leg = parameters.get('leg')

        if (
                not parameters.get('parent') or
                not leg or
                leg not in ['left_node', 'right_node'] or
                not new_user_name or
                not points
        ):
            return bad_request()

        if isinstance(points, int) and points > 0:
            pass
        else:
            context['status'] = False
            context['message'] = 'Параметр points должен быть целым положительным числом'
            return JsonResponse(context)

        if BinaryTree.objects.filter(user=new_user_name).exists():
            context['status'] = False
            context['message'] = 'Пользователь {} уже существует'.format(new_user_name)
            return JsonResponse(context)

        username = parameters.get('parent')
        if username:
            try:
                node = BinaryTree.objects.get(user=username)
            except BinaryTree.DoesNotExist:
                context['status'] = False
                context['message'] = 'Родителя {} не существует'.format(username)
                return JsonResponse(context)
        else:
            return bad_request()

        if getattr(node, leg):
            context['status'] = False
            context['message'] = 'У пользователя {} место {} занято'.format(username, leg.split('_')[0])
            return JsonResponse(context)

        new_node = BinaryTree(
            user=new_user_name,
            parent=node,
        )
        new_node.save()
        setattr(node, leg, new_node.pk)
        node.save(update_fields=(leg,))

        set_points = SetPoints(new_node, points)
        set_points.set_points()

        context['status'] = True
        context['message'] = 'Пользователь {} успешно добавлен в дерево'.format(new_user_name)

        return JsonResponse(context)


@method_decorator(csrf_exempt, name='dispatch')
class PointsHistoryAPIView(View):
    """
    Получение истории начисления баллов
    ПАРАМЕТРЫ В BODY (JSON)
    user:
        all - для всех пользователей
        username - имя пользователя для которого нужно выгрузить историю
    page:
        int - номер страницы для пагинации
    """

    def post(self, request, api_key):
        context = {}

        if not is_valid_api_key(api_key):
            context['status'] = False
            context['message'] = TOKEN_NOT_VALID_MESSAGE
            return JsonResponse(context)

        parameters = get_parameters(self.request.body)
        if not parameters:
            return bad_request()

        user = parameters.get('user')
        page = parameters.get('page')

        if page and isinstance(page, int):
            pass
        else:
            context['status'] = False
            context['message'] = 'Параметр page должен быть целым положительным числом'
            return JsonResponse(context)

        if not user:
            context['status'] = False
            context['message'] = 'Параметр user является обязательным'
            return JsonResponse(context)

        if user == 'all':
            history = BinaryPointsHistory.objects.all()
        else:
            try:
                tree_node = BinaryTree.objects.get(user=user)
            except BinaryTree.DoesNotExist:
                context['status'] = False
                context['message'] = 'Пользователя {} не существует'.format(user)
                return JsonResponse(context)

            history = BinaryPointsHistory.objects.filter(tree_node=tree_node)

        paginator = Paginator(history, APP_SETTINGS.pages_paginator)

        if page > paginator.num_pages:
            context['status'] = False
            context['message'] = 'Страницы {} не существует'.format(page)
            return JsonResponse(context)

        context['status'] = True
        context['count_items'] = paginator.count
        context['count_pages'] = paginator.num_pages
        context['current_page'] = page

        history_list = []
        paginator_page = paginator.page(page)

        if paginator_page.has_next():
            context['next_page'] = paginator_page.next_page_number()

        if paginator_page.has_previous():
            context['previous_page'] = paginator_page.previous_page_number()

        for i in paginator_page:

            history_dict = {
                'username': i.tree_node.user,
                'created': i.created,
            }

            if i.left_points:
                history_dict['left_points'] = i.left_points
            else:
                history_dict['right_points'] = i.right_points

            history_list.append(history_dict)

        context['points_history'] = history_list

        return JsonResponse(context)


@method_decorator(csrf_exempt, name='dispatch')
class StatusAPIView(View):
    """
    Список статусов пользователей бинара
    """

    def post(self, request, api_key):
        context = {}

        if not is_valid_api_key(api_key):
            context['status'] = False
            context['message'] = TOKEN_NOT_VALID_MESSAGE
            return JsonResponse(context)

        statuses_list = []
        for i in STATUS_CHOICES:
            statuses_list.append({
                'id': i[0],
                'title': i[1],
            })

        context['status'] = True
        context['statuses'] = statuses_list
        return JsonResponse(context)
