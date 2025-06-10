import { CommonModule } from '@angular/common';
import { Component, ElementRef, ViewChild, OnInit, ViewChildren, QueryList, AfterViewChecked, HostListener } from '@angular/core';
import { FormControl, FormsModule, ReactiveFormsModule } from '@angular/forms';
import { ChatbotService } from '../services/chatbot.service';
import { NgSelectModule } from '@ng-select/ng-select';
import { ActivatedRoute, Router, RouterModule } from '@angular/router';
import { ErrorSnackbarComponent } from '../utils/error-snackbar/error-snackbar.component';
import { StudyProgramService } from '../services/study-program.service';
import { StudyProgram } from '../data/study-program';
import { environment } from '../../environments/environment';
import { SuccessSnackbarComponent } from '../utils/success-snackbar/success-snackbar.component';
import { EventService } from '../services/event.service';

export interface ChatMessage {
  message: string;
  type: string;
}

export const MESSAGES = {
  en: {
    welcomeMessage: `
      Welcome to the TUM Academic Advisor Chatbot!
      
      I'm here to help you with detailed and accurate information about your studies at the TUM School of Computation, Information and Technology. Whether you have questions about your courses, exams, or study plans, feel free to ask!
      
      If you'd like program-specific advice, please select your study program from the dropdown menu at the top, and I'll provide you with the most relevant information.
    `,
    errorMessage: `Sorry, but I am currently unable to answer your questions. Please try again at a later time.`,
    placeholder: `Enter your message here...`,
    dropdownLabel: `Select Study Program`,
    warningMessage: `may make mistakes. Please verify important information.`,
  },
  de: {
    welcomeMessage: `
      Willkommen beim TUM Academic Advisor Chatbot!
      
      Ich bin hier, um Ihnen mit detaillierten und genauen Informationen zu Ihrem Studium an der TUM School of Computation, Information and Technology zu helfen. Egal ob Sie Fragen zu Kursen, Prüfungen oder Studienplänen haben, zögern Sie nicht zu fragen!
      
      Wenn Sie studiengangspezifische Ratschläge benötigen, wählen Sie bitte Ihr Studienprogramm aus dem Dropdown-Menü oben, und ich werde Ihnen die relevantesten Informationen bereitstellen.
    `,
    errorMessage: `Entschuldigung, aber ich kann Ihre Fragen derzeit nicht beantworten. Bitte versuchen Sie es später erneut.`,
    placeholder: `Geben Sie hier Ihre Nachricht ein...`,
    dropdownLabel: `Studiengang auswählen`,
    warningMessage: `kann Fehler machen. Bitte verifizieren Sie wichtige Informationen.`,
  }
};

@Component({
  selector: 'app-chat',
  standalone: true,
  imports: [
    CommonModule,
    RouterModule,
    FormsModule,
    NgSelectModule,
    ReactiveFormsModule,
    ErrorSnackbarComponent,
    SuccessSnackbarComponent
  ],
  providers: [ChatbotService],
  templateUrl: './chat.component.html',
  styleUrls: ['./chat.component.scss']
})
export class ChatComponent implements OnInit, AfterViewChecked {
  @ViewChild('chatBody', { static: false }) chatBody: ElementRef | undefined;
  @ViewChild('messageInput') messageInput!: ElementRef;
  @ViewChildren('messageElements') messageElements!: QueryList<ElementRef>;
  @ViewChild('errorSnackbar') errorSnackbar!: ErrorSnackbarComponent;
  @ViewChild('successSnackbar') successSnackbar!: SuccessSnackbarComponent;

  chatbotUrl: string = environment.chatbotUrl;
  companyUrl: string = environment.chatbotUrl;

  messages: ChatMessage[] = [];
  userMessage: string = '';
  placeholderText: string = '';
  welcomeMessage: string = '';
  errorMessage: string = '';
  dropdownLabel: string = '';
  warningMessage: string = '';

  studyPrograms: StudyProgram[] = [];
  selectedStudyProgram: StudyProgram | null = null;

  language: 'en' | 'de' = 'en'; // Default language is English
  private needScrollToBottom: boolean = false;
  disableSending: boolean = false;

  private readonly widthBreakpoint = 600;
  isLargeScreen: boolean = true;

  constructor(
    private chatbotService: ChatbotService, 
    private studyProgramService: StudyProgramService, 
    private route: ActivatedRoute,
    private eventService: EventService,
    private router: Router
  ) { }

  ngOnInit() {
    // Get language from route data (or query params if applicable)
    this.studyProgramService.getStudyPrograms().subscribe({
      next: (studyPrograms) => {
        this.studyPrograms = studyPrograms.sort((a, b) => {
          if (a.name < b.name) return -1;
          if (a.name > b.name) return 1;
          return 0;
        });
      },
      error: (error) => {
        this.successSnackbar.dismiss();
        this.errorSnackbar.showError('Studiengänge konnten nicht geladen werden. Bitte versuchen Sie es zu einem späteren Zeitpunkt erneut.', 5000);
      }
    });

    this.route.data.subscribe(data => {
      this.language = data['language'] || 'en';
      this.setLanguageContent();
    });

    this.updatePlaceholderText(window.innerWidth);

    this.messages.push({ message: this.welcomeMessage, type: 'system' });
  }

  ngAfterViewChecked() {
    if (this.needScrollToBottom) {
      this.scrollToBottom();
      this.needScrollToBottom = false;
    }
  }

  setLanguageContent() {
    this.welcomeMessage = MESSAGES[this.language].welcomeMessage;
    this.errorMessage = MESSAGES[this.language].errorMessage;
    this.placeholderText = MESSAGES[this.language].placeholder;
    this.dropdownLabel = MESSAGES[this.language].dropdownLabel;
    this.warningMessage = MESSAGES[this.language].warningMessage;
  }

  updatePlaceholderText(width: number): void {
    if (width <= this.widthBreakpoint) {
      this.isLargeScreen = false;
      this.placeholderText = '';
    } else {
      this.isLargeScreen = true;
      this.placeholderText = MESSAGES[this.language].placeholder;
    }
  }

  // Listen for window resize events
  @HostListener('window:resize', ['$event'])
  onResize(event: Event) {
    const target = event.target as Window;
    this.updatePlaceholderText(target.innerWidth);
  }

  onKeyDown(event: KeyboardEvent): void {
    if (
      event.key === 'Enter' &&
      !event.shiftKey &&
      !event.ctrlKey &&
      !event.altKey &&
      !event.metaKey &&
      !this.disableSending
    ) {
      event.preventDefault(); // Prevents the default action of adding a newline
      this.sendMessage();
    }
  }

  sendMessage() {
    if (this.userMessage.trim()) {
      // Add the user's message to the messages array
      this.disableSending = true;
      this.messages.push({ message: this.userMessage, type: 'user' });
      this.userMessage = '';
      this.resetTextAreaHeight();
      this.needScrollToBottom = true;

      // Study program name in request format
      const selectedProgramName = this.selectedStudyProgram?.name
        .toLowerCase()
        .replace(/\s+/g, '-') || '';

      // Add a loading message to indicate the bot is typing
      const loadingMessage: ChatMessage = { message: '', type: 'loading' };
      this.messages.push(loadingMessage);
      this.needScrollToBottom = true;

      const nonLoadingMessages = this.messages.filter(msg => msg.type !== 'loading');
      // Keep only the last 5 messages, if there are 5 or more
      const messagesToSend = nonLoadingMessages.slice(-5);

      // Call the bot service with the filtered messages
      this.chatbotService.getBotResponse(messagesToSend, selectedProgramName).subscribe({
        next: (response: any) => {
          // Remove the loading message
          this.messages.pop();
          // Add the bot's response
          const formattedResponse = this.formatResponseText(response.answer);
          this.messages.push({ message: formattedResponse, type: 'system' });
          this.needScrollToBottom = true;
          this.disableSending = false;
        },
        error: (error: any) => {
          // Remove the loading message
          this.messages.pop();
          // Add an error message
          this.messages.push({
            message: this.errorMessage,
            type: 'system'
          });
          this.needScrollToBottom = true;
          this.disableSending = false;
          if (error.message && error.message === 'TokenMissing') {
            this.successSnackbar.dismiss();
            this.errorSnackbar.showError('Ihre Session ist abgelaufen. Bitte melden Sie sich erneut an.', 5000);
          }
        }
      });
    }
  }

  formatResponseText(text: string): string {
    const withLineBreaks = text.replace(/(\d+\.\s*\*\*.*?\*\*)/g, '<br>$1');
    const boldFormatted = withLineBreaks.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    const linkFormatted = boldFormatted.replace(/\[(.*?)\]\((.*?)\)/g, '<a href="$2" target="_blank" rel="noopener noreferrer" class="system-link">$1</a>');
    return linkFormatted;
  }

  adjustTextAreaHeight(event: Event): void {
    const textarea = event.target as HTMLTextAreaElement;

    // Reset height to calculate new height correctly
    textarea.style.height = 'auto';

    const computed = window.getComputedStyle(textarea);
    const lineHeight = parseFloat(computed.lineHeight);
    const paddingTop = parseFloat(computed.paddingTop);
    const paddingBottom = parseFloat(computed.paddingBottom);
    const borderTop = parseFloat(computed.borderTopWidth);
    const borderBottom = parseFloat(computed.borderBottomWidth);

    // Calculate the maximum height (4 lines of text)
    const maxHeight = (lineHeight * 4) + paddingTop + paddingBottom + borderTop + borderBottom;

    // Calculate the new height
    const newHeight = Math.min(textarea.scrollHeight, maxHeight);

    // Set the new height
    textarea.style.height = `${newHeight}px`;

    // Handle overflow
    if (textarea.scrollHeight > maxHeight) {
      textarea.style.overflowY = 'auto';
    } else {
      textarea.style.overflowY = 'hidden';
    }
  }

  resetTextAreaHeight(): void {
    if (this.messageInput) {
      const textarea = this.messageInput.nativeElement as HTMLTextAreaElement;

      // Reset the height back to a single line
      const computed = window.getComputedStyle(textarea);
      const lineHeight = parseFloat(computed.lineHeight);
      const paddingTop = parseFloat(computed.paddingTop);
      const paddingBottom = parseFloat(computed.paddingBottom);
      const borderTop = parseFloat(computed.borderTopWidth);
      const borderBottom = parseFloat(computed.borderBottomWidth);

      const singleLineHeight = lineHeight + paddingTop + paddingBottom + borderTop + borderBottom;

      textarea.style.height = `${singleLineHeight}px`;
      textarea.style.overflowY = 'hidden';
    }
  }

  protected scrollToBottom(): void {
    setTimeout(() => {
      if (this.messageElements && this.chatBody && this.messageElements.length > 0) {
        const lastMessageElement = this.messageElements.last;
        lastMessageElement.nativeElement.scrollIntoView({ behavior: 'smooth', block: 'end' });

        setTimeout(() => {
          this.chatBody!.nativeElement.scrollTop += 12;
        }, 500);
      }
    }, 0);
  }

  onProgramChange(program: StudyProgram | null): void {
    this.selectedStudyProgram = program;
  }

  /**
   * Feedback functionality
   */
  shouldShowFeedback(index: number): boolean {
    return index > 0 && this.messages[index].type === 'system';
  }

  sendFeedback(index: number, positive: boolean): void {
    const eventType = positive
      ? 'chat_feedback_positive'
      : 'chat_feedback_negative';

    let question = '';
    for (let i = index - 1; i >= 0; i--) {
      if (this.messages[i].type === 'user') {
        question = this.messages[i].message;
        break;
      }
    }

    const answer = this.messages[index].message;

    const metadata = JSON.stringify({
      question,
      answer
    });

    this.errorSnackbar.dismiss();
    this.successSnackbar.showMessage("Vielen Dank für dein Feedback!", 3000);

    this.eventService.logEvent(eventType, metadata).subscribe({
      error: err => console.warn('Feedback log failed', err)
    });
  }

  /**
   * Privacy and imprint
   */
  onClickDatenschutz() {
    this.router.navigate(['/datenschutz']);
    /*} else {
    this.router.navigate(['/datenschutz']);
    }*/
  }
  
  onClickImpressum() {
    if (this.language === "en") {
      this.router.navigate(['/imprint']);
    } else {
      this.router.navigate(['/impressum']);
    }
  }
}
