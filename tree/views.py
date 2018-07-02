from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from .models import (
    BinaryTree,
)
from settings.models import Setting
import json
from .utils import SetPoints


def is_valid_api_key(api_key):
    """
    Проверка на вилидность API ключа
    :param api_key:
    :return: bool
    """
    my_api_key = Setting.objects.first().api_secret_key
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
            context['message'] = 'Не верный API токен'
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
        nodes = node.get_descendants(include_self=True)

        for i in nodes:
            tree.append({
                'id': i.id,
                'user': i.user,
                'parent': str(i.parent) if i.parent else False,
                'level': i.level,
                'left_node': i.left_node if i.left_node else False,
                'right_node': i.right_node if i.right_node else False,
                'left_points': i.left_points,
                'right_points': i.right_points,
                'status': i.status,
                'created': i.created,
            })

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
            context['message'] = 'Не верный API токен'
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
