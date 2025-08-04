from pydantic_settings import BaseSettings


class EnvConfig(BaseSettings):
    class Config:
        env_file = (".env.local", ".env")
        env_file_encoding = "utf-8"
        env_nested_delimiter = "__"
        extra = "ignore"


class _Bot(EnvConfig, env_prefix="bot_"):
    token: str = ""
    debug: bool = False
    prefix: str = "/"


class _Guild(EnvConfig, env_prefix="guild_"):
    id: int = 803123133015261285


class _Channels(EnvConfig, env_prefix="channels_"):
    welcome: int = 803752961360265236
    rules: int = 1271552038123081728
    select_class: int = 815094070900031530
    announcements: int = 803354070479667271

    general: int = 803123133015261288
    internships: int = 803124244514603008
    resources: int = 803692370323046480
    takeaways: int = 879428355848536176
    goodreads: int = 879429471084613752
    sfsu_opportunities: int = 1229553878941564963


class _Categories(EnvConfig, env_prefix="categories_"):
    administration: int = 803458341543346237
    information: int = 804071122806112277
    general: int = 803123133015261286
    coordinators: int = 1057885537396064298
    tutors: int = 1057883563695013968
    discussion_leaders: int = 1183212478495203458
    csc215: int = 1057886582100721715
    csc220: int = 803139816589623296
    csc340: int = 803139929226870785
    lounge: int = 803458032109355050


Bot = _Bot()
Guild = _Guild()
Channels = _Channels()
Categories = _Categories()
