TODO:
- tell_json method (issue with bytes)
- conserve types over transmission


0.1.8 (2017-10-28)
++++++++++++++++++

- Added tell_list
- Fixed infinite connection looping when adding two socrecievers with same name


0.1.7 (2017-04-04)
++++++++++++++++++

- Implemented connect parameter in SocReceiver
- Fixed bug on key being compared to instance Byt
- Fixed bug with 'key' keyword in tell_key


0.1.4 (2017-04-03)
++++++++++++++++++

- Added hostname to SocReceiver
- Added tell_key method to SocTransmitter to send any key-type of dictionary


0.1.2 (2017-03-22)
++++++++++++++++++

- Made timeout parameter of acknowledgement of receipt accessible


0.1.1 (2017-03-09)
++++++++++++++++++

- Improved high-frequency management of communications
- Changed maximum communication frequency to 100 Hz; faster communications are merged


0.1.0 (2017-03-05)
++++++++++++++++++

- Initial release
