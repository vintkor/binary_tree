from django.db.transaction import atomic


class SetPoints:
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
