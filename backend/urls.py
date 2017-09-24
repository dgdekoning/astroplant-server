from django.conf.urls import include, url
from rest_framework import viewsets, mixins, routers, renderers, documentation
from rest_framework.authtoken import views as authtokenviews
from rest_framework.decorators import detail_route

from backend import models
from backend import permissions

class ObtainAuthToken(authtokenviews.ObtainAuthToken):
    """
    Test!
    """
    renderer_classes = (renderers.JSONRenderer, renderers.BrowsableAPIRenderer,)
    pass

class KitViewSet(viewsets.GenericViewSet,
                 mixins.ListModelMixin,
                 mixins.RetrieveModelMixin):
    """
    list:
    List all kits the user has access to. A human user has access to all kits it owns,
    whereas a kit user has access only to itself.

    retrieve:
    Return the given kit, if the user has access to it.
    """
    def get_queryset(self):
        """
        Get a queryset of all kits the user has access to.
        """

        user = self.request.user
        if isinstance(user, models.Kit):
            return models.Kit.objects.filter(pk=user.pk)
        else:
            return models.Kit.objects.filter(users=user.pk)

    serializer_class = models.KitSerializer

class ExperimentViewSet(viewsets.GenericViewSet,
                        mixins.ListModelMixin,
                        mixins.RetrieveModelMixin):
    """
    list:
    List all experiments the user has access to. A human user has access to experiments
    of all kits it owns. A kit user has access to its experiments.

    retrieve:
    Return the given experiment, if the user has access to it.
    """
    def get_queryset(self):
        """
        Get a queryset of all experiments the user has access to.
        """
        return models.Experiment.objects.all()
        user = self.request.user
        if isinstance(user, models.Kit):
            return models.Experiment.objects.filter(kits=user.pk)
        else:
            kits = models.Kit.objects.filter(users=user.pk)
            return models.Experiment.objects.filter(kits=kits)

    serializer_class = models.ExperimentSerializer

class SensorTypeViewSet(viewsets.GenericViewSet,
                        mixins.ListModelMixin,
                        mixins.RetrieveModelMixin):
    queryset = models.SensorType.objects.all()
    serializer_class = models.SensorTypeSerializer

class MeasurementViewSet(viewsets.GenericViewSet,
                         mixins.ListModelMixin,
                         mixins.RetrieveModelMixin,
                         mixins.CreateModelMixin):
    queryset = models.Measurement.objects.all()
    serializer_class = models.MeasurementSerializer
    permission_classes = [permissions.IsMeasurementOwner,]

router = routers.DefaultRouter()
router.register(r'kits', KitViewSet, base_name='kit')
router.register(r'experiments', ExperimentViewSet, base_name='experiment')
router.register(r'sensor-types', SensorTypeViewSet)
router.register(r'measurements', MeasurementViewSet)

urlpatterns = [
    #url(r'^api-auth/', include('rest_framework.urls',
    #                           namespace='rest_framework')),
    url(r'^api/auth/', ObtainAuthToken.as_view(), name='obtain_token'),
    url(r'^api-docs/', documentation.include_docs_urls(title='AstroPlant API')),
    url(r'^channels-api/', include('channels_api.urls')),
    url(r'^api/', include(router.urls))
]
