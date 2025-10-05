import { Component, EventEmitter, Output, Input, SimpleChanges, OnChanges, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatInputComponent } from '../mat-input/mat-input.component';
import { ButtonComponent } from '../button/button.component';
import { FieldsetComponent } from '../fieldset/fieldset.component';
import { ThemeService } from '../../theme.service';
import { MatListComponent } from '../mat-list/mat-list.component';

@Component({
  selector: 'app-form',
  imports: [CommonModule, MatListComponent, FieldsetComponent, MatInputComponent, ButtonComponent],
  templateUrl: './form.component.html',
  styleUrl: './form.component.css'
})
export class FormComponent implements OnChanges, OnInit {
  @Input() formData: any | any[] = [];
  @Input() formName: string = '';

  @Output() bottoneCliccato = new EventEmitter<string>();
  @Output() formInviato = new EventEmitter<void>();
  @Output() datiAggiornati = new EventEmitter<{ [key: string]: string }>();

  forms: {
    componenti: string[];
    contenuti: any[];
    indice: number;
  }[] = []

  datiFormCorrenti: { [key: string]: string } = {};
  currentIndex: number = 0;
  bottoneFinale: any = null;
  bottoneAbilitato: boolean = false;
  inputStatus: { [id:string]: boolean} = {};
  
  constructor(private themeService: ThemeService) { }

  ngOnInit(): void {
    this.themeService.applyTheme();
    this.themeService.setBodyClass('form')
  }

ngOnChanges(changes: SimpleChanges): void {
  if (!changes['formData'] || !this.formData?.components) return;

  this.forms = [];
  this.bottoneFinale = null;
  this.currentIndex = 0;

  const componentsArray = Array.isArray(this.formData.components)
    ? this.formData.components
    : [this.formData.components];

  let stepIndex = 0;

  const componentiSingle: string[] = [];
  const contenutiSingle: any[] = [];

  for (const comp of componentsArray) {
    const componente = comp.element;

    if (componente === 'button') {
      this.bottoneFinale = { ...comp };
      continue;
    }

    // Per gestire i form che devono apparire a step
    if (componente === 'form' && Array.isArray(comp.components)) {
      const componentiForm: string[] = [];
      const contenutiForm: any[] = [];

      for (const child of comp.components) {
        componentiForm.push(child.element === 'form' ? 'fieldset' : child.element);
        const { element, ...rest } = child;
        contenutiForm.push({ contenuto: rest });
      }

      this.forms.push({
        componenti: componentiForm,
        contenuti: contenutiForm,
        indice: stepIndex++
      });
    } else {
      componentiSingle.push(componente);
      const { element, ...rest } = comp;
      contenutiSingle.push({ contenuto: rest });
    }
  }

  //Per mostrare tutti i componenti che non sono form in una pagina sola
  if (componentiSingle.length > 0) {
    this.forms.unshift({
      componenti: componentiSingle,
      contenuti: contenutiSingle,
      indice: stepIndex++
    });
  }
}
onBottoneClick(id: string) {
    this.bottoneCliccato.emit(id);
}

updateFormData(data: { [key: string]: string }) {
  this.datiFormCorrenti = { ...this.datiFormCorrenti, ...data };
  this.datiAggiornati.emit(this.datiFormCorrenti);
}

goBack(index: number) {
  if (index <= this.currentIndex) {
    this.currentIndex = index;
  }
}

campiCompilati : number = 0;

onInputCompilato(event: {id: string, valido: boolean}) {
  this.inputStatus[event.id]=event.valido;
  this.bottoneAbilitato = Object.values(this.inputStatus).every(v => v === true)
}
}
