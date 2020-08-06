import os


class XFormat:
    INT_SIZE = 4
    BYTE_ORDER = 'little'
    EXTENSION = '.xformat'
    ENCODING = 'utf-8'

    DATA_TYPE_BYTES = 0
    DATA_TYPE_INT = 1
    DATA_TYPE_UTF8_STRING = 2
    DATA_TYPE_LIST = 3
    DATA_TYPE_DICT = 4

    @classmethod
    def serialize_string(cls, s: str) -> bytes:
        record_data = s.encode(encoding=cls.ENCODING)
        return record_data

    @classmethod
    def deserialize_string(cls, bs: bytes) -> str:
        return bs.decode(encoding=cls.ENCODING)

    @classmethod
    def serialize_int(cls, n: int) -> bytes:
        record_data = n.to_bytes(
            length=cls.INT_SIZE,
            byteorder=cls.BYTE_ORDER,
            signed=True,
        )

        return record_data

    @classmethod
    def deserialize_int(cls, bs: bytes) -> int:
        return int.from_bytes(bs, byteorder=cls.BYTE_ORDER, signed=True)

    @classmethod
    def serialize_obj(cls, obj) -> (bytes, bytes):
        obj_type = type(obj)
        if obj_type == int:
            return bytes([cls.DATA_TYPE_INT]), cls.serialize_int(obj)
        elif obj_type == str:
            return bytes([cls.DATA_TYPE_UTF8_STRING]), cls.serialize_string(obj)
        elif obj_type == bytes:
            return bytes([cls.DATA_TYPE_BYTES]), obj
        elif obj_type == list:
            buffer = io.BytesIO()

            for value in obj:
                datatype, encoded_value = cls.serialize_obj(value)
                buffer.write(datatype)
                buffer.write(cls.serialize_int(len(encoded_value)))
                buffer.write(encoded_value)

            return bytes([cls.DATA_TYPE_LIST]), buffer.getvalue()
        elif obj_type == dict:
            buffer = io.BytesIO()

            for key in obj:
                datatype, encoded_key = cls.serialize_obj(key)
                buffer.write(datatype)
                buffer.write(cls.serialize_int(len(encoded_key)))
                buffer.write(encoded_key)

                datatype, encoded_value = cls.serialize_obj(obj[key])
                buffer.write(datatype)
                buffer.write(cls.serialize_int(len(encoded_value)))
                buffer.write(encoded_value)

            return bytes([cls.DATA_TYPE_DICT]), buffer.getvalue()
        else:
            raise Exception(f'Unsupported type {obj_type}!')
            return 0

    @classmethod
    def deserialze_obj(cls, bs: bytes, datatype: int):
        if datatype == cls.DATA_TYPE_BYTES:
            return bs
        elif datatype == cls.DATA_TYPE_INT:
            return cls.deserialize_int(bs)
        elif datatype == cls.DATA_TYPE_UTF8_STRING:
            return cls.deserialize_string(bs)
        elif datatype == cls.DATA_TYPE_LIST:
            retval = []
            buffer = io.BytesIO(bs)
            pos = 0
            bs_len = len(bs)

            while pos < bs_len:
                value_datatype = bs[pos]
                pos += 1

                if(pos + cls.INT_SIZE) > bs_len:
                    raise Exception(f'Broken serialized data!')
                value_byte_count = cls.deserialize_int(bs[pos:pos+cls.INT_SIZE])  # noqa
                pos += cls.INT_SIZE

                if(pos + value_byte_count) > bs_len:
                    raise Exception(f'Broken serialized data!')
                value = cls.deserialze_obj(bs[pos:pos+value_byte_count], value_datatype)  # noqa
                retval.append(value)
                pos += value_byte_count

            return retval
        elif datatype == cls.DATA_TYPE_DICT:
            retval = {}
            buffer = io.BytesIO(bs)
            pos = 0
            bs_len = len(bs)

            while pos < bs_len:
                key_datatype = bs[pos]
                pos += 1

                if (pos + cls.INT_SIZE) > bs_len:
                    raise Exception(f'Broken serialized data!')
                key_byte_count = cls.deserialize_int(bs[pos:pos+cls.INT_SIZE])
                pos += cls.INT_SIZE

                if(pos + key_byte_count) > bs_len:
                    raise Exception(f'Broken serialized data!')
                key = cls.deserialze_obj(bs[pos:pos+key_byte_count], key_datatype)  # noqa
                pos += key_byte_count

                value_datatype = bs[pos]
                pos += 1

                if(pos + cls.INT_SIZE) > bs_len:
                    raise Exception(f'Broken serialized data!')
                value_byte_count = cls.deserialize_int(bs[pos:pos+cls.INT_SIZE])  # noqa
                pos += cls.INT_SIZE

                if(pos + value_byte_count) > bs_len:
                    raise Exception(f'Broken serialized data!')
                value = cls.deserialze_obj(bs[pos:pos+value_byte_count], value_datatype)  # noqa
                pos += value_byte_count

                retval[key] = value

            return retval
        else:
            raise Exception(f'Unsupported data type {datatype}!')
