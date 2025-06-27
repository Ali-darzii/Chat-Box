from celery import shared_task
import logging
from django.db import IntegrityError as UniqueError


logger = logging.getLogger("django")


@shared_task(queue="private_boxes")
def create_private_box(user_id:int):
    """ Create private boxes after user created """
    # circular import
    from private_module.models import PrivateBox
    from auth_module.models import User
    logger.info(f"Creating private box for user {user_id} started ...")

    all_users = User.objects.all().exclude(id=user_id)
    private_boxes = []
    for user in all_users:
        private_boxes.append(
            PrivateBox(first_user_id=user_id, second_user_id=user.id)
        )
    try:
        PrivateBox.objects.bulk_create(private_boxes, ignore_conflicts=True)
    except UniqueError as e:
        logger.error(f"UniqueError user id: {user_id} \n\n {e}")

    except Exception as e:
        logger.critical(f"UnknownError user_id: {user_id} \n\n {e}")

    logger.info(f"Creating private box for user {user_id} Finished.")


