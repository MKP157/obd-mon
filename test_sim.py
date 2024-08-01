import obd
conn = obd.OBD(input("Type serial connection: "), baudrate=115200, )
res = conn.query(obd.commands.SPEED)
print(res)

