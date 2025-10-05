import { Component, EventEmitter, Output, Input, SimpleChanges, OnChanges, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatInputComponent } from '../mat-input/mat-input.component';
import { ButtonComponent } from '../button/button.component';
import { ThemeService } from '../../theme.service';
import { MatListComponent } from '../mat-list/mat-list.component';

@Component({
  selector: 'app-fieldset',
  imports: [CommonModule, MatListComponent, MatInputComponent, ButtonComponent],
  templateUrl: './fieldset.component.html',
  styleUrl: './fieldset.component.css'
})
export class FieldsetComponent {
  @Input() fieldsetData: any | any[] = [];

  @Output() bottoneCliccato = new EventEmitter<string>();
  @Output() formInviato = new EventEmitter<void>();
  @Output() datiAggiornati = new EventEmitter<{ [key: string]: string }>(); 

  forms: {
    componenti: string[];
    nomi: string[];
    contenuti: any[];
    indice: number;
  }[] = []

  datiFormCorrenti: { [key: string]: string } = {};
  currentIndex: number = 0;
  bottoneFinale: any = null;

  constructor(private themeService: ThemeService) { }

  ngOnInit(): void {
    this.themeService.applyTheme();
    this.themeService.setBodyClass('fieldset')
  }

  ngOnChanges(changes: SimpleChanges): void {
    if (changes['fieldsetData'] && this.fieldsetData?.components) {
      this.forms=[];
      
      let index = 0;

      for (const comp of this.fieldsetData.components) {
        const componente = comp.element;
        const nome = comp.name;
        const contenuto = {...comp};
        delete contenuto['element'];

        this.forms.push({
          componenti: [componente],
          nomi: [nome],
          contenuti: [{contenuto}],
          indice: index++
        })
      }

      this.currentIndex = 0;
    }
  }

  onBottoneClick(id: string) {
    this.bottoneCliccato.emit(id);
  }

  updateFormData(data: { [key: string]: string }) {
    this.datiFormCorrenti = { ...this.datiFormCorrenti, ...data };
    this.datiAggiornati.emit(this.datiFormCorrenti);
  }
}
