# XFormat

New data serialization format (because other formats are terrible)

- JSON - cannot be appended on the fly
- YAML - specification is too large
- TFRecord/protobuf - I cannot find where is the specification. They just tell me how great the technology is and there are only samples on using TFRecord with TensorFlow and it is terribly slow. I want to be able to use pure Python without TensorFlow. In addition, the whole TensorFlow graph thing makes it imposible to debug. I think they JIT compile my code for using with CUDA or native DLLs. I'm not gonna live with those specification limitations!

It's not going to be human readable because we need to store binary data.

- Format specification: _1 byte_ for data type (byte, utf-8 encoded string, list, int, etc.) +  _4 bytes_ for data length in bytes and followed by the data.
- There will be only list and records will be stacked one after other. In order to serialize a dictionary: (after you specified the dictionary type in the first byte of the record and the data size (4 bytes)) write the key and then the value, key and value are treated as 2 records in list. It's user's job to most of the parsing and converting to required data type.
- If the data length is 0 but there is still data left then they are treated as metadata. You will need to ship your parsing and converting code for the blob.
- number of bytes to store the record length is 4 bytes (32 bits)
