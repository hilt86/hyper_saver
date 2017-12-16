### Hyper_saver

[Hyper.sh](https://www.hyper.sh) containers make a great devops workstation for a number of reasons:

1. You can shut them down when not in use which saves money and also reduces the attack surface.
2. Hyper.sh containers have a private Layer 2 segment which can be firewalled using [security groups](https://docs.hyper.sh/Feature/network/sg.html) and which are not shared with other customers.
3. Hyper containers have better isolation than Docker containers (hardware isolation, just like a VM) 

However starting your devops workstation every time you start the day is painful, that is why I created a little python script that uses osquery to start up my workstation when I plug in my yubikey.

## Requirements

1. OSQuery (not sure if you just need the python module or the binary as I have both)
2. python (tested on 2.7)
3. A Yubikey, however you can change the script to use any usb device

## Running

hyper_saver takes two arguments :

```
> hyper_saver.py containerName fipName
```

Where containerName is the name you have given your Hyper.sh container and the fipName is the name given to your floating IP!

## TODO

1. Currently there isn't any error handling
2. Integrating a cli library like click would make this utility more easy to use perhaps
3. Submit a pull request if you want to contribute
