import logging
import sys
import asyncio
import traceback
from backend.classes.munchlax import Munchlax
import backend.pokedecoder as pokedecoder

class Bizhawk:
    def __init__(self, host, port, bh):
        super().__init__()
        self.host = host
        self.port = port
        self.bizhawks = {}
        self.bizhawks_status = {}
        self.server = None
        self.is_connected = False
        self.disconnect_lock = asyncio.Lock()
        self.bh = bh

        self.logger = self.init_logging()

    def init_logging(self):
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)

        logging_formatter = logging.Formatter('[%(asctime)s] %(levelname)s: %(message)s')

        file_handler = logging.FileHandler('./logs/bizhawk.log', 'w')
        file_handler.setFormatter(logging_formatter)
        logger.addHandler(file_handler)

        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setFormatter(logging_formatter)
        logger.addHandler(stream_handler)

        return logger
    
    async def handle_bizhawk(self, reader, writer):
        client_id = None
        try:
            # id_length = int((await reader.read(2)).decode())
            client_id = (await self.receive_messages(reader)).decode()
            self.bizhawks[client_id] = writer
            self.bizhawks_status[client_id] = 'connected'
            self.logger.info(f"Emulator {client_id} connected.")

            def get_length():
                if edition > 10 and edition < 20:
                    return 331
                elif edition < 30:
                    return 362
                elif edition < 40:
                    return 601
                else:
                    return 1418

            def update_teams(team):
                team = pokedecoder.team(team, edition)
                teams = self.munchlax.bizhawk_teams
                if player in teams:
                    if teams[player] == team:
                        return
                teams[player] = team
                self.munchlax.unsorted_teams[player] = team

            # edition_length = int((await reader.read(2)).decode())
            edition = int((await self.receive_messages(reader)).decode())

            player = int(client_id[7:])

            length = get_length()
            msg = await reader.read(length)
            update_teams(msg)
            while True:
                try:
                    msg = await reader.read(length)
                    update_teams(msg)
                except Exception as err:
                    self.logger.error(f"handle_bizhawk abgebrochen: {type(err)},{err}")
                    self.logger.error(f"{traceback.format_exc()}")
                    break
        except Exception as err:
            self.logger.error(f"handle_bizhawk abgebrochen: {type(err)},{err}")
            self.logger.error(f"{traceback.format_exc()}")

        await self.disconnect(client_id)

    async def disconnect(self, client_id):
        if client_id in self.bizhawks:
            self.bizhawks[client_id] = None
            self.bizhawks_status[client_id] = False
    
    async def start(self, munchlax):
        self.server = await asyncio.start_server(
            self.handle_bizhawk, self.host, self.port)

        self.munchlax: Munchlax = munchlax

        self.is_connected = True
        async with self.server:
            await self.server.serve_forever()
    
    async def stop(self):
        if self.server:
            self.server.close()
            await self.server.wait_closed()
            
            self.server = None
            self.is_connected = False
            
            self.port = self.bh['port']
            self.logger.info("Bizhawk has been stopped.")

    async def receive_messages(self, reader):
        length = b''
        flag = True
        while flag:
            data = await reader.read(1)
            if not data:
                return None
            if data.decode() != " ":
                length += data
            else:
                flag = False
        length = int(length.decode())

        result = await reader.read(length)

        return result


    async def stop_and_terminate(self, bizhawk_instances):
        await self.stop()

        for bizhawk in bizhawk_instances:
            bizhawk.terminate()