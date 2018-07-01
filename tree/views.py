from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from .models import (
    BinaryTree,
    BinaryPointsHistory,
)
from settings.models import Setting
import json


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
        'status': 0,
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
            context['status'] = 0
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
                context['status'] = 0
                context['message'] = 'Пользователя {} не существует'.format(username)
                return JsonResponse(context)
        else:
            return bad_request()


        context['status'] = 1

        return JsonResponse(context)


@method_decorator(csrf_exempt, name='dispatch')
class SetUserInBinaryAPIView(View):
    """
    Добавление пользователя в бинарное дерево
    ПАРАМЕТРЫ В BODY (JSON)
    auto:
        1 - Автоматическое постановка пользователя в систему
    parent:
        username - Логин родителя
    leg:
        left_node - Поставить пользователя в левую ногу
        right_node - Поставить пользователя в правую ногу
    """

    def post(self, request, api_key):
        context = {}

        if not is_valid_api_key(api_key):
            context['status'] = 0
            context['message'] = 'Не верный API токен'
            return JsonResponse(context)

        parameters = get_parameters(self.request.body)
        if not parameters:
            return bad_request()

        print('-'*80)
        print(parameters)

        context['status'] = 1

        return JsonResponse(context)
