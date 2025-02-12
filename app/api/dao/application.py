from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload

from app.api.models import Application
from app.api.dao.base import BaseDAO
from app.database import async_session_maker


class ApplicationDAO(BaseDAO):
    model = Application

    async def get_applications_by_user(self, user_id: int):
        """
        Возвращает все заявки пользователя по user_id с дополнительной информацией
        о мастере и услуге.

        Аргументы:
            user_id: Идентификатор пользователя.

        Возвращает:
            Список заявок пользователя с именами мастеров и услуг.
        """
        async with async_session_maker() as session:
            try:
                # Используем joined load для ленивой загрузки связанных объектов
                query = (
                    select(self.model)
                    .options(
                        joinedload(self.model.master), joinedload(self.model.service)
                    )
                    .filter_by(user_id=user_id)
                )
                result = await session.execute(query)
                application = result.scalars().all()
                # Возвращаем список словарей с нужными полями
                return [
                    {
                        "application_id": app.id,
                        "service_name": app.service.service_name,  # Название услуги
                        "master_name": app.master.master_name,  # Имя мастера
                        "appointment_date": app.appointment_date,
                        "appointment_time": app.appointment_time,
                        "gender": app.gender.value,
                    }
                    for app in application
                ]
            except SQLAlchemyError as e:
                print(f"Error while fetching applications for user {user_id}: {e}")
                return None

    async def get_all_applications(self):
        """
        Возвращает все заявки в базе данных с дополнительной информацией о мастере и услуге.

        :return:
            Список всех заявок с именами мастеров и услуг.
        """
        async with async_session_maker() as session:
            try:
                # Используем joinedload для загрузки связанных данных
                query = select(self.model).options(
                    joinedload(self.model.master), joinedload(self.model.service)
                )
                result = await session.execute(query)
                application = result.scalars().all()
                # Возвращаем список словарей с нужными полями
                return [
                    {
                        "application_id": app.id,
                        "user_id": app.user_id,
                        "service_name": app.service.service_name,  # Название услуги
                        "master_name": app.master.master_name,  # Имя мастера
                        "appointment_date": app.appointment_date,
                        "appointment_time": app.appointment_time,
                        "client_name": app.client_name,  # Имя клиента
                        "gender": app.gender.value,  # Пол клиента
                    }
                    for app in application
                ]

            except SQLAlchemyError as e:
                print(f"Error while fetching all applications: {e}")
                return None
