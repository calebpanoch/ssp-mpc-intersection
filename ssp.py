def encode_name(name):
    new_name = ""
    for char in name.lower():
        
        if ord(char) == ord(' '):
            new_name = new_name + "27"
            print(char, "27")
        else:
            new_name = new_name + str(ord(char)-96)
            print(char, str(ord(char)-96))
            
    #while len(new_name) < 19:
    #    new_name = new_name + "27"
    return int(new_name)