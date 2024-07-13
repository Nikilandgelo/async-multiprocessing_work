from sqlmodel import Field, SQLModel



class People(SQLModel, table = True):
    
    id: int = Field(primary_key=True)
    birth_year: str = Field()
    eye_color: str = Field()
    films: str = Field(nullable = False)
    gender: str = Field()
    hair_color: str = Field()
    height: str = Field()
    homeworld: str = Field()
    mass: str = Field()
    name: str = Field(nullable = False, unique=True)
    skin_color: str = Field()
    species: str = Field()
    starships: str = Field()
    vehicles: str = Field()