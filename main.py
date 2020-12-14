def function_one():
    return " --- Executing function_one"
	

def function_two():
    return " --- Executing function_two"
	

def function_three():
    return " --- Executing function_three"
	

def switcher(case: int):
    switcher = {
        1: function_one,
        2: function_two,
        3: function_three
    }
    func = switcher.get(case, lambda: "Switcher error")
    func()
	

if __name__ == '__main__':
	print("Menu :");
	entry_names = { "entry 1", "entry 2", "entry 3" };

	for i in range(len(entry_names)):
		print("Entry " + str(i + 1) + " : " + entry_names[i]);

	entry_number = -1;
	while True:
		try:
			print("Numéro de l'entrée désirée : ");
			entry_number = int(input());
		except ValueError:
			print("Erreur : La réponse donnée n'est pas un nombre.");
			break;
		if entry_number > len(entry_names) or entry_number <= 0:
			print("Erreur : La réponse donnée n'est pas dans la liste.");
			break;

	print("Vous avez sélectionné l'exo " + str(entry_number) + " : " + str(entry_names[entry_number - 1]));
	switcher(entry_number)
