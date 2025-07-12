from pydantic import BaseModel, model_validator
from typing import Optional

class NegocioDto(BaseModel):
    # Campo opcional: estado_id puede ser None
    estado_id: Optional[int] = None  
    usuario_id:int
    nombre: str
    categoria_id: int
    correo: str
    telefono: str
    direccion: str
    facebook: str
    instagram: str
    twitter: str
    tiktok: str
    mapa: str
    descripcion: str

    @model_validator(mode='after')
    def validar_nombre(self):
        if not self.nombre or len(self.nombre.strip()) < 2:
            raise ValueError('nombre', 'El campo nombre debe tener al menos 2 caracteres')
        return self

"""
{
    "nombre":"Pastelería los aromos",
    "categoria_id":1,
    "usuario_id":1,
    "estado_id":1,
    "correo":"pollitos@gmail.com",
    "telefono":"123456",
    "direccion":"su casa en el árbol",
    "facebook":"https://web.facebook.com/cesar.cz/",
    "instagram":"https://www.instagram.com/cesar_webmaster/",
    "twitter":"https://x.com/cesar_cz",
    "tiktok":"https://www.tiktok.com/@cesar_webmaster",
    "mapa":"<iframe src='https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d53507.80801038904!2d-71.61104854999999!3d-33.05020045!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x9689dde3de20cec7%3A0xeb0a3a8cbfe19b76!2sValpara%C3%ADso!5e0!3m2!1ses-419!2scl!4v1668632146895!5m2!1ses-419!2scl' width='800' height='500' style='border:0;' allowfullscreen='' loading='lazy' referrerpolicy='no-referrer-when-downgrade'></iframe>",
   "descripcion":"Y, viéndole don Quijote de aquella manera, con muestras de tanta tristeza, le dijo: Sábete, Sancho, que no es un hombre más que otro si no hace más que otro. Todas estas borrascas que nos suceden son señales de que presto ha de serenar el tiempo y han de sucedernos bien las cosas; porque no es posible que el mal ni el bien sean durables, y de aquí se sigue que, habiendo durado mucho el mal, el bien está ya cerca. Así que, no debes congojarte por las desgracias que a mí me suceden, pues a ti no te cabe parte dellas.Y, viéndole don Quijote de aquella manera, con muestras de tanta tristeza, le dijo: Sábete, Sancho, que no es un hombre más que otro si no hace más que otro. Todas estas borrascas que nos suceden son señales de que presto ha de serenar el tiempo y han de sucedernos bien las cosas; porque no es posible que el mal ni el bien sean durables, y de aquí se sigue que, habiendo durado mucho el mal, el bien está ya cerca. Así que, no debes congojart"
}
"""
