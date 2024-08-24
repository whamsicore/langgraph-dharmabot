# Esquema do Banco de Dados Neo4j

## Rótulos de Nós

- Counter
- Conversation
- Message
- User
- Agent

## Tipos de Relacionamentos

- HAS_MESSAGE
- SENT

## Propriedades dos Nós

### Counter

- count: Long

### Conversation

- id: String
- created_at: DateTime

### Message

- id: String
- content: String
- timestamp: DateTime

### User

- id: String

### Agent

- id: String

