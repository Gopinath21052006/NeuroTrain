/* 
Electron      : Create a desktop window  
app           : Controls Application 
BrowserWindow : Creates and Manages app windows 
Path          : Handling file paths  
*/ 

//electron\main.js
const {app, BrowserWindow} = require('electron');
const path = require('path');

// Window Creation 
function createWindow(){
  const win = new BrowserWindow({
    width:1024,    //Initaial width
    height:768,    //Initial height
    webPreferences:{
      preload:path.join(__dirname,'preload.js')  // Security bridge
    }
  });
  win.loadURL('http://localhost:5173'); //react dev server 
}

// Application lifeCycle Management 
app.whenReady().then(()=>{
  createWindow();
  app.on('activate',function(){
    if(BrowserWindow,getAllWindows().length === 0) createWindow();
  });
});

// Ouit Behavior 
app.on('window-all-closed',function(){
  if (process.platform !=='darwin') app.quit()
});