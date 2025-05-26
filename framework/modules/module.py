from framework.loader import Loader, Value, Validators

loader = Loader()
loader.Config(
    Value(
        "log_level",
        "Уровень логирования приложения",
        "INFO",
        validator=Validators.String
    ),
    Value(
        "max_connections",
        "Максимальное количество подключений",
        100,
        validator=Validators.Int
    )
)


@loader.module
class SettingsModule:
    @loader.command(description="Получить текущие настройки")
    async def get_settings():
        log_level = loader.config.get("log_level")
        max_connections = loader.config.get("max_connections")
        return {
            "log_level": log_level,
            "max_connections": max_connections
        }

    @loader.command(description="Изменить уровень логирования")
    async def set_log_level(new_level: str):
        if Validators.String(new_level):
            loader.config.values["log_level"].value = new_level
            loader.save_config()
            return f"Уровень логирования изменен на: {new_level}"
        else:
            return "Ошибка: Уровень логирования должен быть строкой."

    @loader.command(description="Изменить максимальное количество подключений")
    async def set_max_connections(new_max):
        try:
            new_max = int(new_max)
            if Validators.Int(new_max):
                loader.config.values["max_connections"].value = new_max
                loader.save_config()
                return f"Максимальное количество подключений изменено на: {new_max}"
            else:
                return "Ошибка: Максимальное количество подключений должно быть целым числом."
        except ValueError:
            return "Ошибка: Введите корректное целое число."
