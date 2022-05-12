#include <stdio.h>
#include <string.h>



int main(int argc,char **argv)

{
  int mybytes;
  int checkSum;
  FILE *file_FD;
  int file_size;
  int loopSize;
  int i;
  int *piStack12;
  
  piStack12 = &argc;
  file_FD = (FILE *)0x0;
  checkSum = 0;
  file_FD = fopen(argv[1],"r+");
  if (file_FD != (FILE *)0x0) {
     fseek(file_FD,0,2);
     file_size = ftell(file_FD);
     //printf("0x%08x\n", file_size);
     loopSize = (file_size >> 2) - 1;
     fseek(file_FD,0,0);
     for (i = 0; i < 10; i = i + 1) {
        fread(&mybytes,4,1,file_FD);
        //printf("0x%08x\n", mybytes);
        checkSum = checkSum + mybytes;
        //printf("Summe 0x%08x\n", checkSum);
     }
     checkSum = 0x55aa55aa - checkSum;
     printf("0x%08x\n", checkSum);
     fwrite(&checkSum,4,1,file_FD);
  }
  if (file_FD != (FILE *)0x0) {
     fclose(file_FD);
  }
  return 0;
}