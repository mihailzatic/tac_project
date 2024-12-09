import tkinter as tk
from tkinter import messagebox

class AFD:
    def __init__(self, states, alphabet, transitions, start_state, accept_states):
        self.states = states
        self.alphabet = alphabet
        self.transitions = transitions
        self.start_state = start_state
        self.accept_states = accept_states


def process_minimization(afd):
    # partitionare initiala
    partitions = [set(afd.accept_states), set(afd.states) - set(afd.accept_states)]

    # functie pentru identificarea grupului unei stari
    def find_partition(state):
        for group in partitions:
            if state in group:
                return group
        return None

    # gruparea pe subpartitii
    while True:
        new_partitions = []
        for group in partitions:
            sub_groups = {}
            for state in group:
                # crearea de semnatura pentru fiecare stare
                signature = tuple(
                    frozenset(find_partition(afd.transitions.get(state, {}).get(symbol, None)) or set())
                    for symbol in afd.alphabet
                )
                sub_groups.setdefault(signature, set()).add(state)
            new_partitions.extend(sub_groups.values())

        if new_partitions == partitions:
            break
        partitions = new_partitions

    # mapam starile minimizate
    state_mapping = {}
    minimized_states = set()
    for group in partitions:
        representative = sorted(group)[0]  # setam reprezentantul ca fiind primul intalnit alfabetic
        for state in group:
            state_mapping[state] = representative
        minimized_states.add(representative)

    # crearea tranzitii minimizate
    minimized_transitions = {}
    for group in partitions:
        representative = sorted(group)[0]
        minimized_transitions[representative] = {}
        for symbol in afd.alphabet:
            target_state = afd.transitions.get(representative, {}).get(symbol)
            if target_state is not None:
                minimized_transitions[representative][symbol] = state_mapping[target_state]

    # setarea starii de start si a starii(starilor) acceptoare
    minimized_start_state = state_mapping[afd.start_state]
    minimized_accept_states = {state_mapping[state] for state in afd.accept_states}

    # sortarea starilor
    minimized_states = sorted(minimized_states)

    return AFD(minimized_states, afd.alphabet, minimized_transitions, minimized_start_state, minimized_accept_states)


class AFDMinimizerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AFD Minimizer")

        self.states_label = tk.Label(root, text="States (comma-separated):")
        self.states_label.grid(row=0, column=0, padx=10, pady=5)
        self.states_entry = tk.Entry(root)
        self.states_entry.grid(row=0, column=1, padx=10, pady=5)

        self.alphabet_label = tk.Label(root, text="Alphabet (comma-separated):")
        self.alphabet_label.grid(row=1, column=0, padx=10, pady=5)
        self.alphabet_entry = tk.Entry(root)
        self.alphabet_entry.grid(row=1, column=1, padx=10, pady=5)

        self.accept_states_label = tk.Label(root, text="Accept States (comma-separated):")
        self.accept_states_label.grid(row=2, column=0, padx=10, pady=5)
        self.accept_states_entry = tk.Entry(root)
        self.accept_states_entry.grid(row=2, column=1, padx=10, pady=5)

        self.start_state_label = tk.Label(root, text="Start State:")
        self.start_state_label.grid(row=3, column=0, padx=10, pady=5)
        self.start_state_entry = tk.Entry(root)
        self.start_state_entry.grid(row=3, column=1, padx=10, pady=5)

        self.create_table_button = tk.Button(root, text="Create Transition Table", command=self.create_transition_table)
        self.create_table_button.grid(row=4, column=0, columnspan=2, pady=10)

        self.table_frame = None
        self.transition_entries = {}

    def create_transition_table(self):
        states = self.states_entry.get().split(",")
        alphabet = self.alphabet_entry.get().split(",")
        if not states or not alphabet:
            messagebox.showerror("Error", "Please enter valid states and alphabet.")
            return

        if self.table_frame:
            self.table_frame.destroy()
        self.table_frame = tk.Frame(self.root)
        self.table_frame.grid(row=5, column=0, columnspan=2, pady=10)

        tk.Label(self.table_frame, text="States / Symbols").grid(row=0, column=0, padx=5, pady=5)
        for j, symbol in enumerate(alphabet):
            tk.Label(self.table_frame, text=symbol).grid(row=0, column=j + 1, padx=5, pady=5)

        self.transition_entries = {}
        for i, state in enumerate(states):
            tk.Label(self.table_frame, text=state).grid(row=i + 1, column=0, padx=5, pady=5)
            self.transition_entries[state] = {}
            for j, symbol in enumerate(alphabet):
                entry = tk.Entry(self.table_frame, width=5)
                entry.grid(row=i + 1, column=j + 1, padx=5, pady=5)
                self.transition_entries[state][symbol] = entry

        self.minimize_button = tk.Button(self.root, text="Minimize AFD", command=self.minimize_afd)
        self.minimize_button.grid(row=6, column=0, columnspan=2, pady=10)

    def minimize_afd(self):
        states = self.states_entry.get().split(",")
        alphabet = self.alphabet_entry.get().split(",")
        accept_states = self.accept_states_entry.get().split(",")
        start_state = self.start_state_entry.get()

        if not states or not alphabet or not accept_states or not start_state:
            messagebox.showerror("Error", "Please fill all fields.")
            return

        transitions = {}
        for state in states:
            transitions[state] = {}
            for symbol in alphabet:
                value = self.transition_entries[state][symbol].get()
                if value:
                    transitions[state][symbol] = value

        afd = AFD(set(states), set(alphabet), transitions, start_state, set(accept_states))
        minimized_afd = process_minimization(afd)

        self.show_minimized_afd(minimized_afd)

    def show_minimized_afd(self, afd):
        output_window = tk.Toplevel(self.root)
        output_window.title("Minimized AFD")

        table_frame = tk.Frame(output_window)
        table_frame.pack(padx=10, pady=10)

        columns = list(afd.alphabet)
        tk.Label(table_frame, text="States / Symbols").grid(row=0, column=0, padx=5, pady=5)
        for j, symbol in enumerate(columns):
            tk.Label(table_frame, text=symbol).grid(row=0, column=j + 1, padx=5, pady=5)

        for i, state in enumerate(afd.states):
            tk.Label(table_frame, text=state).grid(row=i + 1, column=0, padx=5, pady=5)

            for j, symbol in enumerate(afd.alphabet):
                transition_value = afd.transitions[state].get(symbol, "")
                entry = tk.Entry(table_frame, width=5)
                entry.grid(row=i + 1, column=j + 1, padx=5, pady=5)
                entry.insert(tk.END, transition_value)
                entry.config(state=tk.DISABLED)

        start_label = tk.Label(output_window, text=f"Start State: {afd.start_state}")
        start_label.pack(pady=5)

        accept_label = tk.Label(output_window, text=f"Accept States: {', '.join(afd.accept_states)}")
        accept_label.pack(pady=5)

if __name__ == "__main__":
    root = tk.Tk()
    app = AFDMinimizerApp(root)
    root.mainloop()
