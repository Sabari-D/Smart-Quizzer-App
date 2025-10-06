import { Component, OnInit } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { PopupComponent } from './popup/popup';
import { CommonModule } from '@angular/common';
import { PopupService } from './services/popup';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet, PopupComponent, CommonModule],
  templateUrl: './app.html',
  styleUrls: ['./app.css'],
})
export class App implements OnInit {
  popupVisible = false;
  popupMessage = '';
  popupIsError = false;

  constructor(private popupService: PopupService) {}

  ngOnInit() {
    this.popupService.popupState$.subscribe((state: { message: string, isError: boolean }) => {
      this.popupMessage = state.message;
      this.popupIsError = state.isError;
      this.popupVisible = true;
    });
  }

  hidePopup() {
    this.popupVisible = false;
  }
}