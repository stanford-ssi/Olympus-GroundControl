# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: cmd.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


import nanopb_pb2 as nanopb__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\tcmd.proto\x12\x0fquail_telemetry\x1a\x0cnanopb.proto\"\xc6\x03\n\x07Message\x12\x10\n\x08sequence\x18\x01 \x02(\r\x12)\n\x06reboot\x18\x02 \x01(\x0b\x32\x17.quail_telemetry.rebootH\x00\x12/\n\tstart_udp\x18\x03 \x01(\x0b\x32\x1a.quail_telemetry.start_udpH\x00\x12?\n\x11request_metaslate\x18\x04 \x01(\x0b\x32\".quail_telemetry.request_metaslateH\x00\x12\x41\n\x12response_metaslate\x18\x05 \x01(\x0b\x32#.quail_telemetry.response_metaslateH\x00\x12/\n\tset_field\x18\x06 \x01(\x0b\x32\x1a.quail_telemetry.set_fieldH\x00\x12#\n\x03\x61\x63k\x18\x07 \x01(\x0b\x32\x14.quail_telemetry.ackH\x00\x12\x31\n\nquery_info\x18\x08 \x01(\x0b\x32\x1b.quail_telemetry.query_infoH\x00\x12\x35\n\x0crespond_info\x18\t \x01(\x0b\x32\x1d.quail_telemetry.respond_infoH\x00\x42\t\n\x07message\"\x08\n\x06reboot\"\x05\n\x03\x61\x63k\"5\n\tstart_udp\x12\x0c\n\x04\x61\x64\x64r\x18\x01 \x02(\r\x12\x0c\n\x04port\x18\x02 \x02(\r\x12\x0c\n\x04hash\x18\x03 \x02(\x04\"!\n\x11request_metaslate\x12\x0c\n\x04hash\x18\x01 \x02(\x04\"=\n\x12response_metaslate\x12\x0c\n\x04hash\x18\x01 \x02(\x04\x12\x19\n\tmetaslate\x18\x02 \x02(\x0c\x42\x06\x92?\x03\x08\xe8\x07\"\x8a\x01\n\tset_field\x12\x0c\n\x04hash\x18\x01 \x02(\x04\x12\x0e\n\x06offset\x18\x02 \x02(\r\x12\x14\n\ndata_int16\x18\x03 \x01(\x05H\x00\x12\x15\n\x0b\x64\x61ta_uint32\x18\x04 \x01(\rH\x00\x12\x14\n\ndata_float\x18\x05 \x01(\x02H\x00\x12\x13\n\tdata_bool\x18\x06 \x01(\x08H\x00\x42\x07\n\x05\x61\x64\x61ta\"\x0c\n\nquery_info\"o\n\x0crespond_info\x12\x13\n\x04name\x18\x01 \x02(\tB\x05\x92?\x02p\x14\x12\x16\n\x07version\x18\x02 \x02(\tB\x05\x92?\x02pd\x12\x32\n\x06slates\x18\x03 \x03(\x0b\x32\x1b.quail_telemetry.slate_infoB\x05\x92?\x02\x10\x05\"=\n\nslate_info\x12\x13\n\x04name\x18\x01 \x02(\tB\x05\x92?\x02p\x14\x12\x0c\n\x04size\x18\x02 \x02(\r\x12\x0c\n\x04hash\x18\x03 \x02(\x04')

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'cmd_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  _RESPONSE_METASLATE.fields_by_name['metaslate']._options = None
  _RESPONSE_METASLATE.fields_by_name['metaslate']._serialized_options = b'\222?\003\010\350\007'
  _RESPOND_INFO.fields_by_name['name']._options = None
  _RESPOND_INFO.fields_by_name['name']._serialized_options = b'\222?\002p\024'
  _RESPOND_INFO.fields_by_name['version']._options = None
  _RESPOND_INFO.fields_by_name['version']._serialized_options = b'\222?\002pd'
  _RESPOND_INFO.fields_by_name['slates']._options = None
  _RESPOND_INFO.fields_by_name['slates']._serialized_options = b'\222?\002\020\005'
  _SLATE_INFO.fields_by_name['name']._options = None
  _SLATE_INFO.fields_by_name['name']._serialized_options = b'\222?\002p\024'
  _MESSAGE._serialized_start=45
  _MESSAGE._serialized_end=499
  _REBOOT._serialized_start=74
  _REBOOT._serialized_end=82
  _ACK._serialized_start=347
  _ACK._serialized_end=352
  _START_UDP._serialized_start=518
  _START_UDP._serialized_end=571
  _REQUEST_METASLATE._serialized_start=573
  _REQUEST_METASLATE._serialized_end=606
  _RESPONSE_METASLATE._serialized_start=608
  _RESPONSE_METASLATE._serialized_end=669
  _SET_FIELD._serialized_start=672
  _SET_FIELD._serialized_end=810
  _QUERY_INFO._serialized_start=384
  _QUERY_INFO._serialized_end=396
  _RESPOND_INFO._serialized_start=826
  _RESPOND_INFO._serialized_end=937
  _SLATE_INFO._serialized_start=939
  _SLATE_INFO._serialized_end=1000
# @@protoc_insertion_point(module_scope)
