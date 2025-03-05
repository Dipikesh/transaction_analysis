import logging
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import TransactionUpload
from .serializers import TransactionUploadSerializer
from .tasks import analyze_transactions

logger = logging.getLogger(__name__)

class TransactionUploadViewSet(viewsets.ModelViewSet):
    queryset = TransactionUpload.objects.all()
    serializer_class = TransactionUploadSerializer

    def create(self, request, *args, **kwargs):
        try:
            logger.info(f"Received request")
            # Validate file presence
            if 'file' not in request.FILES:
                return Response(
                    {'error': 'No file provided'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            file_obj = request.FILES['file']
            
            # Validate file type
            if not file_obj.name.endswith('.csv'):
                return Response(
                    {'error': 'File must be CSV format'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Create upload record
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            upload = serializer.save()
            
            logger.info(f"File upload received: {upload.id}")

            # Trigger Celery task
            try:
                task = analyze_transactions.delay(upload.id)
                logger.info(f"Celery task queued with ID: {task.id}")
            except Exception as celery_error:
                logger.error(f"Celery task creation failed: {str(celery_error)}")


            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )

        except Exception as e:
            logger.error(f"Error during file upload: {str(e)}")
            return Response(
                {'error': 'Internal server error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['get'])
    def status(self, request, pk=None):
        upload_id = pk or request.query_params.get('id')
        try:
            if upload_id:
                try:
                    upload = TransactionUpload.objects.get(id=upload_id)
                    return Response({
                        'id': upload.id,
                        'status': upload.status,
                        'result': upload.result
                    })
                except TransactionUpload.DoesNotExist:
                    return Response(
                        {'error': f'Upload with id {pk} not found'},
                        status=status.HTTP_404_NOT_FOUND
                    )
            else:
                uploads = TransactionUpload.objects.all()
                return Response([{
                    'id': upload.id,
                    'status': upload.status,
                    'result': upload.result
                } for upload in uploads])
                
        except Exception as e:
            logger.error(f"Error fetching status: {str(e)}")
            return Response(
                {'error': 'Internal server error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )