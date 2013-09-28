from django.db import transaction
from rest_framework import viewsets, routers, serializers, status, mixins
from rest_framework.response import Response

from .models import Job, Spec, JobSpec
from .tasks import process_job


class JobListingField(serializers.RelatedField):
    def to_native(self, value):
        return {
            'id': value.id,
            'version': value.version,
        }


class JobSerializer(serializers.HyperlinkedModelSerializer):
    """ Custom job serializer to rename some fields"""
    created_at = serializers.DateTimeField(source='created')
    updated_at = serializers.DateTimeField(source='modified')
    started_at = serializers.DateTimeField(source='start')
    finished_at = serializers.DateTimeField(source='finish')
    packages = JobListingField(many=True, source='job_specs')

    class Meta:
        model = Job
        fields = ('id', 'url', 'status', 'created_at',
                  'updated_at', 'started_at', 'finished_at', 'packages')


class JobViewSet(mixins.CreateModelMixin, viewsets.ReadOnlyModelViewSet):
    model = Job
    serializer_class = JobSerializer

    def create(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                job = Job.objects.create_from_requirements(request.DATA['requirements'])
                serializer = self.get_serializer(job)
                headers = self.get_success_headers(serializer.data)
        except Exception as e:
            return Response({'requirements': 'Bad requirements. %s' % e},
                            status=status.HTTP_400_BAD_REQUEST)
        else:
            process_job.delay(job.pk)
            return Response(serializer.data, status=status.HTTP_201_CREATED,
                            headers=headers)


router = routers.DefaultRouter()
router.register(r'jobs', JobViewSet)
