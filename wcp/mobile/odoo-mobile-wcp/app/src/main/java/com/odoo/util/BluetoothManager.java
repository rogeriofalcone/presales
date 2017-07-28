/**##############################################################################
 #
 #    OpenERP, Open Source Management Solution
 #    This module copyright (C) 2014 Savoir-faire Linux
 #    (<http://www.savoirfairelinux.com>).
 #
 #    This program is free software: you can redistribute it and/or modify
 #    it under the terms of the GNU Affero General Public License as
 #    published by the Free Software Foundation, either version 3 of the
 #    License, or (at your option) any later version.
 #
 #    This program is distributed in the hope that it will be useful,
 #    but WITHOUT ANY WARRANTY; without even the implied warranty of
 #    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 #    GNU Affero General Public License for more details.
 #
 #    You should have received a copy of the GNU Affero General Public License
 #    along with this program.  If not, see <http://www.gnu.org/licenses/>.
 #
 ############################################################################## */

package com.odoo.util;

import android.bluetooth.BluetoothAdapter;
import android.bluetooth.BluetoothDevice;
import android.bluetooth.BluetoothSocket;
import android.content.Context;
import android.os.Looper;
import android.util.Log;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.util.Set;
import java.util.UUID;


public class BluetoothManager {

    static String TAG = BluetoothManager.class.getSimpleName();

    Context mContext;
    BluetoothAdapter mBluetoothAdapter;
    BluetoothDevice mDevice;
    BluetoothSocket mSocket = null;
    public static InputStream instream = null;
    public static BufferedReader reader;
    Thread inputStreamThread = null;
    boolean paired = false;
    boolean connected = false;
    boolean running = false;

    ReceiveDataListener delegate = mStubReceiver;

    static ReceiveDataListener mStubReceiver = new ReceiveDataListener() {
        @Override
        public void onDataReceived(String line) {

        }

        @Override
        public void onDeviceConnected() {

        }

        @Override
        public void onDeviceDisconnected() {

        }
    };

    final UUID SERIAL_UUID = UUID.fromString("00001101-0000-1000-8000-00805F9B34FB"); // UUID

    public interface ReceiveDataListener {

        public void onDataReceived(String line);

        public void onDeviceConnected();

        public void onDeviceDisconnected();

    }

    public BluetoothManager(Context activity) {
        mContext = activity;
        mBluetoothAdapter = BluetoothAdapter.getDefaultAdapter();
        if (mBluetoothAdapter == null) {
            running = false;
        }
    }

    public void startDataCollection(ReceiveDataListener d) {
        delegate = d;
        startCollection();
        delegate.onDeviceDisconnected();
    }

    public void stopDataCollection() {
        delegate = mStubReceiver;
        running = false;
        connected = false;
        Runnable asyn = new Runnable() {
            @Override
            public void run() {
                try {
                    if(mSocket != null)
                        mSocket.close();
                } catch (IOException e) {
                    e.printStackTrace();
                }
                if (inputStreamThread != null) {
                    try {
                        inputStreamThread.join();
                    } catch (InterruptedException e) {
                        e.printStackTrace();
                    }
                }
            }
        };
        asyn.run();
    }

    /**
     * @param name A portion of the device's name
     * @return
     */
    public boolean deviceHasBeenPaired(String name) {
        Set<BluetoothDevice> pairedDevices = mBluetoothAdapter.getBondedDevices();
        // If there are paired devices
        if (pairedDevices.size() > 0) {
            // Loop through paired devices
            for (BluetoothDevice device : pairedDevices) {
                // mArrayAdapter.add(device.getName() + "\n" + device.getAddress());
                if (device.getName().contains(name)) {
                    paired = true;
                    mDevice = device;
                    return true;
                }
            }
        }
        return false;
    }


    public boolean btIsEnabled() {
        return mBluetoothAdapter.isEnabled();
    }

    private void startCollection() {
        if (paired && !connected) {
            // we've got the device-- open the serial port and go:
            inputStreamThread = new Thread(new Runnable() {

                @Override
                public void run() {
                    Looper.prepare();
                    try {
                        mSocket = mDevice.createRfcommSocketToServiceRecord(SERIAL_UUID);
                        mSocket.connect();
                        instream = mSocket.getInputStream();
                        reader = new BufferedReader(new InputStreamReader(instream));
                        connected = true;

                        delegate.onDeviceConnected();
                    } catch (IOException e) {
                        connected = false;
                        try {
                            mSocket.close();
                        } catch (IOException e1) {
                            e1.printStackTrace();
                        }
                        delegate.onDeviceDisconnected();
                    }

                    while (connected) {
                        try {
                            if (instream.available() > 0) {
                                StringBuffer buffer = new StringBuffer();
                                int ch;
                                while (instream.available() > 0) {
                                    ch = instream.read();
                                    buffer.append((char) ch);
                                }
                                String line = buffer.toString();
                                Log.i(TAG, line);
                                if (delegate != null)
                                    delegate.onDataReceived(line);
                            } else {
                                Thread.sleep(1000, 0);
                            }
                        } catch (IOException e1) {
                            delegate.onDeviceDisconnected();
                            connected = false;
                            return;
                        } catch (InterruptedException e) {
                            e.printStackTrace();
                            delegate.onDeviceDisconnected();
                        }
                    }

                }
            });
            inputStreamThread.start();

        }
    }
}
