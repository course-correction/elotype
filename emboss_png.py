import sys
from PIL import Image
import serial

CMD_NEWLINE = bytearray.fromhex("ff 0d")


def png_to_command(png_file):
    command = bytearray.fromhex("86")
    with Image.open(png_file) as img:
        width, height = img.size
        pixels = img.load()

        last_y = 0
        for y in range(height):
            last_x = -1
            for x in range(width):
                is_black = pixels[x, y] == (0, 0, 0)
                if is_black:
                    if last_x == -1:
                        if last_y != 0:
                            command += CMD_NEWLINE
                        delta_y = y - last_y
                        command += delta_y.to_bytes(2, "big")

                        last_y = y
                        last_x = 0

                    x_delta = x - last_x
                    last_x = x
                    # add last_x as big endian 16-bit integer
                    point = x_delta.to_bytes(2, "big")
                    command += point

    command += bytearray.fromhex("ff 0d 00")
    return command


def send_to_serial(port, data):
    """Sends binary data to a serial device at 9800 baud."""
    try:
        with serial.Serial(port, 9800, timeout=1) as ser:
            ser.write(data)
            print(f"Sent {len(data)} bytes to {port}.")
    except serial.SerialException as e:
        print(f"Error opening serial port: {e}")
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python emboss_png.py <hexdump_file> <serial_port>")
        sys.exit(1)

    file_path = sys.argv[1]
    serial_port = sys.argv[2]

    binary_data = png_to_command(file_path)
    print(binary_data.hex())
    send_to_serial(serial_port, binary_data)
