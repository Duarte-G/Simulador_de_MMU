import sys
from collections import deque

# Classe que implementa a Memory Management Unit (MMU) para tradução de endereços e gerenciamento de memória virtual
class MMU:
    # Inicializa as estruturas de dados para gerenciamento de memória
    def __init__(self, policy):
        self.policy = policy
        self.page_table = {}
        self.tlb = {}
        # Define tamanho máximo da TLB como 16 entradas
        self.tlb_queue = deque(maxlen=16)
        self.memory = {}
        self.page_queue = deque()
        
        # LRU specific
        self.lru_counters = {}
        # Mapeia frames para suas respectivas páginas
        self.frame_to_page = {} 
        
        # Second Chance specific
        self.second_chance = {}
        
        self.tlb_hits = 0
        self.tlb_misses = 0
        self.page_faults = 0

    # Traduz endereço lógico para físico usando tabela de páginas e TLB
    def translate_address(self, logical_address):
        if isinstance(logical_address, str):
            logical_address = int(logical_address, 16)

        # Extrai número da página (20 bits) e deslocamento (12 bits)
        page_number = logical_address >> 12
        offset = logical_address & 0xFFF

        if page_number in self.tlb:
            self.tlb_hits += 1
            frame_number = self.tlb[page_number]
        else:
            self.tlb_misses += 1
            
            if page_number in self.page_table:
                frame_number = self.page_table[page_number]
            else:
                self.page_faults += 1
                frame_number = self.handle_page_fault(page_number)
            
            self.update_tlb(page_number, frame_number)

        if self.policy == "LRU":
            self.update_lru(page_number)
        elif self.policy == "SegundaChance":
            self.update_second_chance(page_number)

        return (frame_number << 12) | offset

    # Gerencia falha de página, implementando substituição quando necessário
    def handle_page_fault(self, page_number):
        if len(self.memory) >= 64:
            if self.policy == "LRU":
                frame_to_remove = self.lru_replacement()
                old_page = self.frame_to_page[frame_to_remove]
                del self.page_table[old_page]
                del self.lru_counters[old_page]
                del self.memory[frame_to_remove]
            else:  # Second Chance
                frame_to_remove = self.second_chance_replacement()
                old_page = self.memory[frame_to_remove]
                del self.page_table[old_page]
                del self.memory[frame_to_remove]
        else:
            frame_to_remove = len(self.memory)

        self.memory[frame_to_remove] = page_number
        self.page_table[page_number] = frame_to_remove
        
        if self.policy == "LRU":
            self.lru_counters[page_number] = 0
            self.frame_to_page[frame_to_remove] = page_number
        else:  # Second Chance
            self.second_chance[frame_to_remove] = 1
            self.page_queue.append(frame_to_remove)

        return frame_to_remove

    # Seleciona página para substituição usando política LRU
    def lru_replacement(self):
        # Encontra a página menos recentemente usada
        lru_page = max(self.lru_counters.items(), key=lambda x: x[1])[0]
        return self.page_table[lru_page]

    # Seleciona página para substituição usando política Segunda Chance
    def second_chance_replacement(self):
        while True:
            oldest_frame = self.page_queue[0]
            if self.second_chance.get(oldest_frame, 0) == 0:
                self.page_queue.popleft()
                return oldest_frame
            else:
                self.second_chance[oldest_frame] = 0
                self.page_queue.append(self.page_queue.popleft())

    # Atualiza contadores LRU para cada página na memória
    def update_lru(self, page_number):
        # Incrementa contador para todas as páginas exceto a atual
        for p in self.lru_counters:
            self.lru_counters[p] += 1
        # Reseta o contador para a página acessada
        if page_number in self.lru_counters:
            self.lru_counters[page_number] = 0

    # Atualiza bit de referência para política Segunda Chance
    def update_second_chance(self, page_number):
        if page_number in self.page_table:
            frame = self.page_table[page_number]
            self.second_chance[frame] = 1

    # Atualiza TLB com nova tradução de página, removendo entrada mais antiga se necessário
    def update_tlb(self, page_number, frame_number):
        if page_number not in self.tlb:
            if len(self.tlb) >= 16:
                oldest_page = self.tlb_queue.popleft()
                del self.tlb[oldest_page]
            
            self.tlb[page_number] = frame_number
            self.tlb_queue.append(page_number)

    # Executa simulação lendo endereços do arquivo trace e coletando estatísticas
    def run_simulation(self, trace_file):
        with open(trace_file, 'r') as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) < 2:
                    continue
                
                logical_address = parts[0]
                self.translate_address(logical_address)

        print(f"TLB Hits: {self.tlb_hits}")
        print(f"TLB Hit Rate: {self.tlb_hits / (self.tlb_hits + self.tlb_misses):.2%}")
        print(f"TLB Misses: {self.tlb_misses}")
        print(f"Page Faults: {self.page_faults}")
        print(f"Page Fault Rate: {self.page_faults / (self.tlb_hits + self.tlb_misses):.2%}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso: python simulador.py <arquivo_trace> <política: LRU ou SegundaChance>")
        sys.exit(1)
    
    trace_file = sys.argv[1]
    policy = sys.argv[2]
    
    if policy not in ["LRU", "SegundaChance"]:
        print("Política inválida! Escolha entre 'LRU' ou 'SegundaChance'")
        sys.exit(1)
    
    mmu = MMU(policy)
    mmu.run_simulation(trace_file)