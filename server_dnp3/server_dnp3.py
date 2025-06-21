# dnp3_server.py
import random
import time
from pydnp3 import opendnp3, asiopal
from pydnp3.opendnp3 import Analog
from pydnp3.asiodnp3 import (
    DNP3Manager,
    PrintingCommandHandler,
    DefaultOutstationApplication,
    OutstationStackConfig,
    DatabaseSizes
)

class MyOutstationApplication(DefaultOutstationApplication):
    def SupportsWriteAbsoluteTime(self):
        return False

class OutstationContext:
    def __init__(self, port=20000):
        self.manager = DNP3Manager(1)
        self.channel = self.manager.AddTCPServer(
            name="server",
            loggerid=opendnp3.levels.ALL,
            retry=asiopal.ChannelRetry.Default(),
            endpoint="0.0.0.0",
            port=port,
            listener=None
        )

        config = OutstationStackConfig(DatabaseSizes(16))
        config.outstation.eventBufferConfig.maxAnalogEvents = 10

        self.outstation = self.channel.AddOutstation(
            name="outstation",
            commandHandler=PrintingCommandHandler(),
            application=MyOutstationApplication(),
            config=config
        )

        self.outstation.Enable()

        for i in range(16):
            value = random.uniform(0.0, 100.0)
            self.outstation.GetDatabase().UpdateAnalog(
                index=i,
                value=Analog(value),
                eventMode=opendnp3.EventMode.Detect
            )

    def simulate(self):
        try:
            while True:
                for i in range(16):
                    value = random.uniform(0.0, 100.0)
                    self.outstation.GetDatabase().UpdateAnalog(
                        index=i,
                        value=Analog(value),
                        eventMode=opendnp3.EventMode.Detect
                    )
                time.sleep(10)
        except KeyboardInterrupt:
            print("Servidor detenido")

if __name__ == '__main__':
    server = OutstationContext()
    server.simulate()
