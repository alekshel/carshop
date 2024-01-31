import rest_framework.pagination


class LimitedPagination(rest_framework.pagination.LimitOffsetPagination):
    default_limit = 10
    max_limit = 100
