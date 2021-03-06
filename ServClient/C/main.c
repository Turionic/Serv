#include <unistd.h>
#include <stdio.h>
#include <sys/socket.h>
#include <stdlib.h>
#include <netinet/in.h>
#include <string.h>
#include <sys/utsname.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <errno.h>
#include <unistd.h>
#include <syslog.h>

#define PORT 25565



void err_sys(const char* x)
{
  perror(x);
  exit(1);
}

int ClientSock(){
  open("Notifier.log", LOG_PID, LOG_DAEMON);
  struct utsname unameData;
  uname(&unameData);

  struct sockaddr_in address;
  int sockfd, ServerReply;
  //char recvline[MAXLINE + 1];
  char buffer[1024] = {0};

  // Creates Socket
  if ( (sockfd = socket(AF_INET, SOCK_STREAM, 0)) < 0){
    syslog(LOG_WARNING,"Socket Error\n");
    closelog();
    return 1;
  }
  memset(&address, 0, sizeof(address));
  address.sin_family = AF_INET;
  address.sin_port = htons(PORT);
  // Sets Socket to IP. Hard coded for now. Will make config file
  if (inet_pton(AF_INET, "73.180.174.252",&address.sin_addr) <= 0){
    syslog(LOG_WARNING,"Could not inet_pton Address");
    closelog();
    return 1;
  }

  if( connect(sockfd, (struct sockaddr *) &address, sizeof(address)) < 0 ){
    syslog(LOG_WARNING,"Connect Error\n");
    closelog();
    return 1;
  }


  char str1[] = "ConnectionTest", str2[] = "Update", str3[] = "Closing Connection", str4[] = "Info";
  char str5[] = "Added";
  // Checks if server replies correctly 
  ServerReply = read( sockfd, buffer, 1024);
  if(strcmp(str1,buffer) != 0){
    syslog(LOG_WARNING,"Unknown Response From Server: ");
    //syslog(LOG_WARNING, "%s\n",buffer);
    closelog();
    return 0;
  }
  char host[80];
  // Sends Hostname for server to see if new client, or update on old
  strcpy(host, unameData.nodename);
  send(sockfd, host, strlen(host), 0);

  ServerReply = read(sockfd, buffer, 1024);
  
  if(strcmp(str2,buffer) == 0){
    syslog(LOG_NOTICE, "Updated Server\n");
    ServerReply = read(sockfd, buffer, 1024);
    //fprintf(log, "Server: %s\n", buffer);
    closelog();
    return 0;
  }

  if(strcmp(str4, buffer) == 0){
    syslog(LOG_NOTICE, "Adding self to Server Databse...");
    // Ugly solution to format data to be sent  
    char data[80];
    strcpy(data, unameData.machine);
    strcat(data, " - ");
    strcat(data, unameData.sysname);
    strcat(data, " - ");
    strcat(data, unameData.version);
    strcat(data, " - ");
    strcat(data, unameData.release);
    strcat(data,"[");
    strcat(data, unameData.nodename);
    send(sockfd, data, strlen(data), 0);
    ServerReply = read(sockfd, buffer, 1024);
    if(strcmp(str5, buffer) == 0){
      syslog(LOG_NOTICE,"Ok\n");
      ServerReply = read(sockfd, buffer, 1024);
      //fprintf(log,"Server: %s\n", buffer);
      closelog();
      return 0;
    }
    else{
      syslog(LOG_WARNING,"Error Adding to Server\n");
      closelog();
      return 1;

    }
  }

  return 0;


  



}



int main(){
   // Sets up to run as daemon 
  
   pid_t pid, sid;

   //Forking
   pid = fork();
   if (pid < 0){
     exit(EXIT_FAILURE);
   }
   if (pid > 0){
     exit(EXIT_SUCCESS);
   }

   umask(0);
  
   
   // Creating sid for child
   sid = setsid();
   if (sid < 0){
       exit(EXIT_FAILURE);
   }
   // Closing file descriptors
   close(STDIN_FILENO);
   close(STDOUT_FILENO);
   close(STDERR_FILENO);
   // Main Loop
   int Placeholder;
   while(1){

     if(ClientSock()){
	 Placeholder = 1;
     }

     
     sleep(3600);
   }
}




