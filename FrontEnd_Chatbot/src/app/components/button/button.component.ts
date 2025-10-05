import { Component, EventEmitter, Output, Input, OnChanges, SimpleChanges } from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-button',
  imports: [FormsModule, CommonModule, MatButtonModule],
  templateUrl: './button.component.html',
  styleUrl: './button.component.css'
})
export class ButtonComponent implements OnChanges {
  @Input() dati: any | any[] = [];
  @Output() bottoneCliccato = new EventEmitter<string>();
  
  buttonData: { id: string, name: string }[] = [];
  @Input() disabled: boolean = false;

  onClick(idBottone: string) {
    this.bottoneCliccato.emit(idBottone)
  }

  ngOnChanges(changes: SimpleChanges): void {
    if (this.dati && changes['dati']) {
      const datiArray = Array.isArray(this.dati) ? this.dati : [this.dati];
      this.buttonData = datiArray.map(btn => ({
        id: btn.id,
        name: btn.name
      }));
    }

  }

}
