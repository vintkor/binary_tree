from django.db.transaction import atomic


class SetPoints:
    """
    Начисление баллов пользователям вверх по бинарному дереву
    """

    def __init__(self, user, points):
        self.__user = user
        self.__points = points

    def __get_ancestors(self):
        self.__user_ancestors = self.__user.get_ancestors(ascending=True, include_self=True)
        search_list = dict()
        for i in self.__user_ancestors:
            search_list[i.id] = dict({
                'user': i,
                'id': i.id,
                'left_node': i.left_node,
                'right_node': i.right_node,
                'left_points': i.left_points,
                'right_points': i.right_points,
                'parent_id': i.parent_id,
            })
        self.__search_list = search_list

    def __check_direction(self, user_id, parent_id):
        if user_id == self.__search_list[parent_id]['left_node']:
            return False
        return True

    def __set_points_list(self):
        points_list = list()
        for i in self.__user_ancestors:
            if i.parent_id:
                parent = self.__search_list[i.parent_id]
                if self.__check_direction(i.id, i.parent_id):
                    points_list.append({
                        'user': parent['user'],
                        'right_points': self.__points,
                    })
                else:
                    points_list.append({
                        'user': parent['user'],
                        'left_points': self.__points,
                    })
        return points_list

    def __init(self):
        self.__get_ancestors()

    def set_points(self):
        self.__init()
        points_list = self.__set_points_list()
        from tree.models import Reason, BinaryPointsHistory
        reason = Reason.objects.get(code=1101)
        with atomic():
            for i in points_list:

                current_node = i['user']

                ph = BinaryPointsHistory()
                ph.tree_node = i['user']
                ph.points = self.__points
                ph.reason = reason

                if i.get('left_points', None):
                    ph.left_points = i['left_points']
                    current_node.left_points += ph.left_points
                else:
                    ph.right_points = i['right_points']
                    current_node.right_points += ph.right_points

                current_node.save()
                ph.save()


class CleanTree:
    """
    Удаление неактивных пользователей из бинарного дерева
    """

    def __init__(self, node):
        self.node = node
        self.children_nodes = self.node.get_descendants()
        self.parent_node = self.node.parent
        self.node_in_parent_leg = None

    def _set_node_in_parent_leg(self):
        """
        Устанавливаем в свойство node_in_parent_leg в какой его ноге находится текущая нода
        """
        if self.node.id == self.parent_node.left_node:
            self.node_in_parent_leg = 'left_node'
        elif self.node.id == self.parent_node.right_node:
            self.node_in_parent_leg = 'right_node'
        else:
            pass

    def is_can_delete_node(self):
        """
        Можем ли мы удалить ноду
        :return: bool
        """
        if len(self.node.get_children()) == 2:
            return False
        else:
            return True

    def _set_new_children_to_parent_node(self, is_up_top):
        """
        Записываем в родительскую ноду нового потомка
        """
        if is_up_top:
            setattr(self.parent_node, self.node_in_parent_leg, self.children_nodes.first().id)
        else:
            setattr(self.parent_node, self.node_in_parent_leg, None)
        self.parent_node.save()

    def _rebuild_tree(self):
        """
        Перестраиваем границы бинарного дерева
        """
        from .models import BinaryTree
        BinaryTree._tree_manager.rebuild()

    def delete_node(self):
        """
        Удаление ноды если это возможно
        :return: str
        """
        node_name = self.node.user
        self._set_node_in_parent_leg()
        if self.is_can_delete_node():

            if len(self.children_nodes) > 0:
                first_child = self.children_nodes[0]
                if first_child:
                    self._set_new_children_to_parent_node(True)
                    first_child.move_to(self.parent_node, position='first-child')
            else:
                self._set_new_children_to_parent_node(False)

            self.node.delete()
            self._rebuild_tree()

            message = 'Нода {} успешно удалена'.format(node_name)
            return message
        else:
            message = 'Ноду {} удалить нельзя, так как у неё 2 потомка'.format(node_name)
            return message
