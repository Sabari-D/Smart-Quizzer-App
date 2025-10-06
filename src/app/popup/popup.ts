import { Component, EventEmitter, Input, Output } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-popup',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './popup.html',
  styleUrls: ['./popup.css']
})
export class PopupComponent {
  @Input() message: string = '';
  @Input() isVisible: boolean = false;
  @Input() isError: boolean = false;
  @Output() close = new EventEmitter<void>();

  closePopup() {
    this.close.emit();
  }
}