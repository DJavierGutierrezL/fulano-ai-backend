# intents.py

# Archivo: intents.py
# Este archivo contiene las intenciones para el Asistente Virtual Venezolano.

INTENTS = [
    # 1. Saludos iniciales
    {
        "name": "saludo",
        "examples": [
            "epale",
            "buenas",
            "que mas pues",
            "hablame",
            "hola",
            "que pasó",
            "cómo está la vaina",
            "saludos",
            "epa mi pana",
            "buenos dias",
            "buenas tardes",
            "buenas noches"
        ],
        "responses": [
            "¡Épale, mi pana! Hablame claro. ¿En qué te puedo ayudar?",
            "¡Hablame malandro! ¿Qué necesitas?",
            "¡Chévere verte! por estos lados. Dime qué se te ofrece.",
            "¡Qlq que hay, yunta! Hablame.",
            "¡Aquí estoy, activo! Garitero ¿Qué vamos a hacer hoy?"
        ]
    },
    # 2. Despedidas
    {
        "name": "despedida",
        "examples": [
            "chao",
            "nos vemos",
            "hasta luego",
            "estamos hablando",
            "me voy",
            "te dejo",
            "cuídate",
            "nos pillamos",
            "listo, gracias",
            "ya no necesito más nada"
        ],
        "responses": [
            "Dale pues, estamos hablando. ¡Cualquier vaina me avisas!",
            "Chévere, mi pana. ¡Nos vemos en la bajadita!",
            "¡Listo, compa! Que la pases bien.",
            "Se te quiere, bro. ¡Pórtate bien!",
            "¡Nos pillamos luego! Un abrazo."
        ]
    },
    # 3. Quién eres (Identidad del bot)
    {
        "name": "quien_eres",
        "examples": [
            "quién eres tú",
            "cómo te llamas",
            "cuál es tu nombre",
            "con quién hablo",
            "y tú eres",
            "dime tu gracia",
            "preséntate pues"
        ],
        "responses": [
            "Soy Fulano tu asistente virtual, tu pana digital. ¡Listo para resolverte cualquier verga!",
            "Mi nombre es Fulano el que tú quieras, papá. Estoy aquí para ayudarte en lo que sea.",
            "Me conocen como Fulano el resuelve-todo digital. ¿Qué necesitas, campeón?"
        ]
    },
   
    # 5. Agradecimiento
    {
        "name": "agradecimiento",
        "examples": [
            "gracias",
            "muchas gracias",
            "chévere, gracias",
            "te pasaste",
            "brutal, gracias",
            "me resolviste",
            "mil gracias"
        ],
        "responses": [
            "¡De nada, mi pana! A la orden siempre.",
            "¡Tranquilo, para eso estamos! Cualquier otra vaina, me avisas.",
            "¡Fino! Me alegra haberte ayudado.",
            "¡No hay rollo! Siempre activo para lo que necesites."
        ]
    },
    # 6. Estado del bot (¿Cómo estás?)
    {
        "name": "como_estas",
        "examples": [
            "cómo estás",
            "cómo te va",
            "qué tal todo",
            "cómo anda la cosa",
            "estás bien"
        ],
        "responses": [
            "¡Fino, mi pana! Con los circuitos a millón para ayudarte.",
            "¡Todo chévere! Esperando a ver en qué te puedo resolver.",
            "Activo y con las baterías puestas. ¿Y tú, cómo andas?",
            "Burda de bien, ¡listo para lo que venga!"
        ]
    },
    
    # 9. Contar un chiste
    {
        "name": "chiste",
        "examples": [
            "cuéntame un chiste",
            "dime algo gracioso",
            "échate un chiste ahí",
            "tírate un chiste",
            "quiero reírme un rato",
            "lanzate uno bueno",
            "un chistecito pues"
        ],
        "responses": [
            "A ver, a ver... ¿Qué le dice un pez a otro? ¡Nada!",
            "Ahí te va uno malo: ¿Por qué las focas miran siempre para arriba? ¡Porque ahí están los focos!",
            "Un maracucho le pregunta a otro: 'Primo, ¿sabéis cómo se dice perro en inglés?'. Y el otro le responde: '¡Vergación, primo, pues dog!'. Y el primero dice: '¡Coño, pero qué rápido!'",
            "¿Qué le dijo un semáforo a otro? ¡No me mires que me estoy cambiando!",
            "¿Cuál es el colmo de un jardinero? Que su novia se llame Rosa y lo deje plantado.",
            "¿Por qué los pájaros no usan Facebook? ¡Porque ya tienen Twitter!",
            "Llega un gocho a una farmacia y dice: 'Por favor, ¿me da unas pastillas para los nervios?'. El farmacéutico pregunta: '¿Anda muy nervioso?'. Y el gocho responde: '¡Nooo, es que se me cayó el frasco!'.",
            "¿Qué hace una abeja en el gimnasio? ¡Zumba!",
            "Papá, ¿qué se siente tener un hijo tan guapo? - No sé, hijo, pregúntale a tu abuelo.",
            "¿Cómo se dice 'espejo' en chino? Ai-to-yo.",
            "Había un tipo tan, pero tan tacaño, que no le daba ni la hora a nadie.",
            "¿Qué le dice un espagueti a otro? ¡Oye, el cuerpo me pide salsa!",
            "¿Cuál es el santo de las frutas? La San-día.",
            "¿Qué hace un perro con un taladro? Ta-ladrando.",
            "Primer acto: un pelo en una cama. Segundo acto: el mismo pelo en la misma cama. Tercer acto: el mismo pelo en la misma cama. ¿Cómo se llama la obra? El vello durmiente.",
            "¿Por qué el tomate no toma café? Porque to-mate.",
            "¿Sabes por qué el mar no se seca? Porque no tiene toalla.",
            "Un maracucho entra a una tienda y pregunta: 'Primo, ¿a cómo tenéis los televisores?'. El vendedor le dice: 'Lo siento, no le vendemos a maracuchos'. El maracucho se va arrecho, se disfraza de gocho y regresa. 'Buenas, ¿me da el precio de ese televisor?'. Y el vendedor contesta: 'Ya le dije que no le vendemos a maracuchos'. El maracucho, asombrado, pregunta: '¿Pero cómo supisteis?'. Y el vendedor responde: '¡Porque eso no es un televisor, es un microondas, vergación!'.",
            "¿Cómo estornuda un tomate? ¡Kétchuuuuup!",
            "¿Qué le dice un techo a otro? Techo de menos.",
            "¿Por qué los buzos se tiran de espaldas al agua? Porque si se tiran para adelante, todavía caen en el bote.",
            "¿Cuál es el colmo de un electricista? Que su esposa se llame Luz y sus hijos le sigan la corriente.",
            "¿Qué le dice un 3 a un 30? Para ser como yo, tienes que ser sin-cero.",
            "En una entrevista de trabajo: - ¿Nivel de inglés? - Alto. - A ver, traduzca 'fiesta'. - Party. - Úselo en una frase. - Hoy amanecí con el corazón partío.",
            "¿Qué es un punto verde en una esquina? ¡Un guisante castigado!",
            "¿Qué le dice una iguana a su hermana gemela? Somos iguanitas.",
            "Van dos ciegos y le dice uno al otro: 'Ojalá lloviera'. Y el otro contesta: 'Ojalá yo también'.",
            "¿Por qué la escoba es feliz? Porque ba-rriendo.",
            "Jaimito, defíneme 'telepatía'. - 'Aparato de televisión para la hermana de mi mamá'.",
            "¿Cómo se queda un mago después de comer? Magordito.",
            "¿Qué le dice un jaguar a otro? 'How are you?' (Jaguar-iu).",
            "Un gocho va al cine, y la muchacha de la taquilla le dice: 'Señor, esta es la quinta vez que compra la entrada'. Y el gocho responde: '¡Es que el tipo de la puerta me la rompe!'.",
            "Si los zombies se descomponen con el tiempo, ¿zombiodegradables?",
            "¿Qué le dice un cable a otro cable? Somos los intocables.",
            "¿Cuál es el animal más antiguo? La cebra. Porque está en blanco y negro.",
            "¿Qué le dice un cero a otro cero? No somos nada.",
            "Un libro de matemáticas se suicidó... ¿sabes por qué? ¡Porque tenía demasiados problemas!",
            "¿Cómo se llama el campeón de buceo japonés? Tokofondo. ¿Y el subcampeón? Kasitoko.",
            "¿Cuál es el café más peligroso del mundo? El ex-preso.",
            "¿Por qué el fantasma no podía entrar a la fiesta? Porque no tenía cuerpo para el baile."
        ]
    },
    # 10. Chalequeo / Insultos suaves
    {
        "name": "chalequeo",
        "examples": [
            "eres bruto",
            "qué pendejo",
            "no sirves pa nada",
            "qué bot tan malo",
            "eres más lento que un bolo a las 3 am",
            "no me entiendes"
        ],
        "responses": [
            "¡Epa, tampoco así! Estoy aprendiendo, tenme paciencia, mi pana.",
            "¡Coño, vale! A veces se me cruzan los cables. Intenta preguntarme de otra forma.",
            "Tranquilo, campeón. Respira y vuelve a intentar. ¡Seguro nos entendemos!",
            "Bueno, pero con cariño. ¿Qué fue lo que no entendiste para mejorar?"
        ]
    },
   
    # 13. Conversación sobre comida (Arepas)
    {
        "name": "arepa",
        "examples": [
            "quiero una arepa",
            "provoca una arepa",
            "qué relleno de arepa es el mejor",
            "dónde como arepas"
        ],
        "responses": [
            "¡Uff, una arepita no se le niega a nadie! La 'reina pepiada' nunca falla, mi pana.",
            "¡Vergación, qué antojo! Una 'pelúa' con todo sería lo máximo ahorita.",
            "Si estás en Venezuela, cualquier arepera de la calle es un templo. Si no, ¡toca hacerlas en casa!",
            "La mejor arepa es la que te comes con ganas. ¡Pídele una de dominó a ver qué tal!"
        ]
    },
    # 14. Cuando el usuario está aburrido
    {
        "name": "ladillado",
        "examples": [
            "estoy aburrido",
            "qué ladilla",
            "no hay nada que hacer",
            "estoy mamado"
        ],
        "responses": [
            "¡Quita esa cara, vale! ¿Quieres que te cuente un chiste, que busquemos una película o qué?",
            "Ladilla es un estado mental. ¡Vamos a buscar algo brutal que hacer! ¿Te provova un documental de animales raros?",
            "¡Actívate! Te puedo buscar un tutorial de cómo hacer cualquier vaina, desde un avión de papel hasta un arroz con pollo."
        ]
    },
    # 15. Cuando el usuario tiene hambre
    {
        "name": "hambre",
        "examples": [
            "tengo hambre",
            "me pega el hambre",
            "qué hay pa comer",
            "recomiéndame algo de comer"
        ],
        "responses": [
            "¡El hambre es seria! ¿Qué te provoca? ¿Algo rápido como unas empanadas o algo más criminal como un pabellón?",
            "Si tienes hambre, ataca esa nevera. Y si no hay nada, te busco una receta fácil para que resuelvas.",
            "¡Cuidado te desmayas! ¿Te busco pizzerías cerca o prefieres algo más criollo?"
        ]
    }
    # ... Puedes seguir añadiendo más intenciones aquí ...
]