import { Component } from '@angular/core';

@Component({
  selector: 'app-welcome',
  templateUrl: './welcome.component.html',
  styleUrls: ['./welcome.component.css']
})
export class WelcomeComponent {

  onRegister(): void {
    console.log('Register button clicked!');
  }

  onLogin(): void {
    console.log('Login button clicked!');
  }

  onExit(): void {
    console.log('Exit button clicked!');
  }
}
