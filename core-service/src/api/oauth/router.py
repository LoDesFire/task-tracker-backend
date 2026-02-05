from rest_framework.routers import SimpleRouter

from api.oauth.permissions_view_set import UserPermissionsViewSet

router = SimpleRouter(trailing_slash=False)

router.register("permissions", UserPermissionsViewSet, basename="permissions")
