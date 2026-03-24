PFA (Personal Finance App) to aplikacja służąca do zarządzania wydatkami użytkownika. Logika biznesowa jest stosunkowo prosta – projekt powstał głównie w celu zaprezentowania moich umiejętności w projektowaniu aplikacji backendowych.

Aplikacja ma asynchroniczny backend napisany w fastapi oraz prosty frontend napisany w js (frontend jest symboliczny, wygenerowany glownie przez AI). System jest zintegrowany z Keycloak, a w projekcie zaimplementowałem własną logikę obsługi JWT.

Do przechowywania sesji oraz tokenów wykorzystywany jest Redis, natomiast główną bazą danych jest PostgreSQL.

Aplikacja posiada również asynchroniczny moduł generowania raportów dzialający w celery (rabbitmq jako broker)

Aplikcja jest stale rozwijana Testy są w drodze