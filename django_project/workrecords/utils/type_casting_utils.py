
def cast_int_to_string( input_data, output_bit):
    """
    将一个int转化成为string，并且指定输出的长度。转化后的string长度不足的左侧补0，长度超过的取最后的指定长度位。
    :param input_data 输入的int
    :param output_bit 输出的位数
    """
    output_data = str(input_data)
    bit_difference = output_bit - len(output_data)
    if bit_difference > 0:
        return output_data.rjust(output_bit, "0")
    else:
        return output_data[-output_bit:]