# Simulador de MMU (Memory Management Unit)
Uma implementação em Python de um simulador de Unidade de Gerenciamento de Memória que demonstra políticas de substituição de páginas (LRU e Segunda Chance) com suporte a TLB. Este projeto foi desenvolvido como parte de um trabalho da disciplina de Sistemas Operacionais.

## Funcionalidades
- Tradução de endereços lógicos para físicos usando paginação de um nível
- Implementação de TLB (Translation Lookaside Buffer)
- Duas políticas de substituição de páginas:

    - LRU (Least Recently Used)
    - Segunda Chance

- Suporte para leitura de arquivos de trace com padrões de acesso à memória
- Acompanhamento de estatísticas de desempenho e geração de relatórios CSV

## Como usar
```python
python simulador.py <arquivo_trace> <politica>
```
onde politica pode ser "LRU" ou "SegundaChance"

## Detalhes Técnicos
- Número da página: 20 bits
- Deslocamento: 12 bits
- Tamanho da página: 4 KB
- Tamanho da memória: 64 frames
- Tamanho da TLB: 16 entradas

O simulador processa arquivos de trace contendo endereços hexadecimais e tipos de operação (leitura/escrita) para simular padrões de acesso à memória e comportamento de substituição de páginas.

Este projeto é um exemplo educacional e pode ser usado para entender conceitos básicos de gerenciamento de memória em sistemas operacionais.