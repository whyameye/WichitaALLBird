// compile with gcc -Wall -pedantic -O2 -o dtr dtr.c
// g++ is some sort of option too

#include <sys/ioctl.h> //ioctl() call defenitions
#include <fcntl.h>
#include <time.h>

int main(int argc, char** argv)
{
   int fd;
   fd = open(argv[1],O_RDWR | O_NOCTTY );//Open Serial Port
  
   int RTS_flag;
   RTS_flag = TIOCM_DTR;
   ioctl(fd,TIOCMBIS,&RTS_flag);//Set RTS pin
   ioctl(fd,TIOCMBIC,&RTS_flag);//Clear RTS pin
   close(fd);
}
