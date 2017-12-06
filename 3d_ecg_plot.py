#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys

def ecg_to_matrix():
    return
    # each slice(3):
    #    a = ((data[1] & 0x0F) << 8) | data[0]
    #    b = ((data[1] & 0xF0) << 4) | data[2]
    # [a,b] 

#Each sample is represented by a 16-bit two’s complement amplitude stored least significant byte first. Any unused high-order bits are sign-extended from the most significant bit. Historically, the format used for MIT-BIH and AHA database distribution 9-track tapes was format 16, with the addition of a logical EOF (octal 0100000) and null-padding after the logical EOF.
def parse_dat(hdr):
    return
    

def parse_record_line(line):
    name, num_sig, freq, *rest = line.split()
    name, *num_segments = name.split('/')
    if len(num_segments) > 0:
        raise "HEA file contains segments not signals: UNSUPPORTED"
    freq, *counter = freq.split('/')
    freq = float(freq)
    num_samp = int(rest[0] or 0)
    return { 'name': name,
             'num_signals': int(num_sig),
             'frequency': freq,
             'samples_per_signal': num_samp }

def parse_signal_line(line):
    skew = offset = units = baseline = None

    datfile, fmt, *rest = line.split()

    # encoding: "FORMATxSAMPLE:SKEW+OFFSET"
    fmt, *frame_samples = fmt.split('x')
    if len(frame_samples) > 0:
        frame_samples, *skew = frame_samples.split(':')
        frame_samples = int(frame_samples)
        if len(skew) > 0:
            skew, *offset = skew.split('+')
            skew = int(skew)
            if len(offset) > 0:
                offset = int(offset[0])

    gain = rest[0]
    # encoding: "GAIN(BASELINE)/UNITS"
    if gain:
        gain, *units = gain.split('/')
        if len(units) > 0 : units = units[0]
        gain, *baseline = gain.split('(')
        gain = float(gain)
        if len(baseline) > 0 : baseline = int(baseline[0][0:-1])

    # ... resolution zero initial-value checksum block_size description
    adc_res = rest[1]
    adc_zero = rest[2]
    init_value = rest[3]
    checksum = rest[4]
    block_size = rest[5]
    description = rest[6]

    return {'datfile': datfile,
            'format': fmt,
            'frame_samples': frame_samples or 1,
            'skew': skew or 0,
            'offset': offset or 0,
            'gain': gain or 0.0,
            'units': units or 'mV',
            'baseline': baseline or 0,
            'adc_resolution': int(adc_res or 12),
            'adc_zero': int(adc_zero or 0),
            'initial_value': int(init_value or adc_zero or 0),
            'checksum': int(checksum or 0),
            'block_size': int(block_size or 0),
            'name': description or ""}

def valid_line(line):
    return (line.strip() and (not line.startswith('#')))

def parse_hea(fname):
    f = open(fname, 'r')
    lines = f.readlines()
    f.close()
    dirname = os.path.dirname(fname)
    if dirname == '': dirname = '.' 

    idx = 0
    while (idx < len(lines)):
        if valid_line(lines[idx]) : break
        idx += 1

    h_rec = parse_record_line(lines[idx])

    # read signal lines
    sigs = []
    for line in [x for x in lines[idx+1:] if valid_line(x)]:
        h_sig = parse_signal_line(line)
        h_sig['filename'] = os.path.join(dirname, h_sig['datfile'])
        sigs.append( h_sig )

    return { 'name': h_rec['name'], 'num_samples': h_rec['samples_per_signal'], 
            'frequency': int(h_rec['frequency']), 
            'signals': sigs[0:h_rec['num_signals']] }

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: %s HEA" % sys.argv[0])
        sys.exit(1)

    hdr = parse_hea(sys.argv[1])
    print(hdr)
    m_ecg = parse_dat(hdr)

# plot matrix
