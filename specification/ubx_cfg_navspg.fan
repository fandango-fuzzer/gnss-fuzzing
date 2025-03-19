# ubx_cfg_navspg.fan by XXX (Anonymized for submission)
import random
import struct

<start> ::= <ubx_message>

<ubx_message> ::= <ubx_header> <ubx_payload> <ubx_checksum>

<ubx_header> ::= <ubx_magic> <ubx_msg_class> <ubx_msg_id> <ubx_msg_len>
<ubx_magic> ::= b'\xb5\x62'
<ubx_msg_class> ::= b'\x06'   # CFG messages
<ubx_msg_id> ::= b'\x8a'      # CFG-VALSET message
<ubx_msg_len> ::= <u2>
    where <ubx_msg_len> == uint16(len(bytes(<ubx_payload>)))

<ubx_payload> ::= <version> <layers> <reserved0> <cfgdata>
<version> ::= b'\x00'
<layers> ::= b'\01'           # RAM only
<reserved0> ::= b'\x00\x00'
<cfgdata> ::= <use_usrdat> <usrdat_maja> <usrdat_flat> \
    <usrdat_dx> <usrdat_dy> <usrdat_dz> <usrdat_rotx> \
    <usrdat_roty> <usrdat_rotz> <usrdat_scale>

<use_usrdat> ::= b'\x25\x00\x11\x10' b'\x01'
<usrdat_maja> ::= b'\x62\x00\x11\x50' <r8_maja>
<usrdat_flat> ::= b'\x63\x00\x11\x50' <r8_flat>
<usrdat_dx> ::= b'\x64\x00\x11\x40' <r4_d>
<usrdat_dy> ::= b'\x65\x00\x11\x40' <r4_d>
<usrdat_dz> ::= b'\x66\x00\x11\x40' <r4_d>
<usrdat_rotx> ::= b'\x67\x00\x11\x40' <r4_rot>
<usrdat_roty> ::= b'\x68\x00\x11\x40' <r4_rot>
<usrdat_rotz> ::= b'\x69\x00\x11\x40' <r4_rot>
<usrdat_scale> ::= b'\x6a\x00\x11\x40' <r4_scale>

<ubx_checksum> ::= <u2>
    where <ubx_checksum> == ubx_checksum(bytes(<ubx_header>), bytes(<ubx_payload>))

<u1> ::= <byte>
<u2> ::= <byte>{2}

<r8_maja> ::= <byte>{8} := make_ieee_double_maja()
<r8_flat> ::= <byte>{8} := make_ieee_double_flat()
<r4_d> ::= <byte>{4} := make_ieee_float_d()
<r4_rot> ::= <byte>{4} := make_ieee_float_rot()
<r4_scale> ::= <byte>{4} := make_ieee_float_scale()

def uint16(n: int) -> bytes:
  return n.to_bytes(2, 'little')

def make_ieee_double_maja() -> bytes:
  # Major axis can be between 6,300,000 and 6,500,000 metres
  return struct.pack('<d', random.uniform(6300000.0, 6500000.0))

def make_ieee_double_flat() -> bytes:
  # Flatness can be between 0 and 500
  return struct.pack('<d', random.uniform(0.0, 500.0))

def make_ieee_float_d() -> bytes:
  # Displacement can be between -5000.0 and +5000.0 metres
  return struct.pack('<f', random.uniform(-5000.0, +5000.0))

def make_ieee_float_rot() -> bytes:
  # Rotation can be between -20.0 and +20.0 milli arcseconds
  return struct.pack('<f', random.uniform(-20.0, +20.0))

def make_ieee_float_scale() -> bytes:
  # Scale can be between 0,0 and 50.0 ppm
  return struct.pack('<f', random.uniform(0.0, +50.0))

def ubx_checksum(header: bytes, payload: bytes) -> bytes:
  ck_a = 0
  ck_b = 0

  for c in (header + payload)[2:]:
    ck_a = (ck_a + c) & 0xff
    ck_b = (ck_b + ck_a) & 0xff

  return bytes([ck_a, ck_b])
