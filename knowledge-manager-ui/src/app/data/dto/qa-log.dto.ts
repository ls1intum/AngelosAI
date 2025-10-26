export interface QaLogDTO {
    id: string;
    createdAt: string;
    question: string;
    answer: string;
    studyProgram: string | null;
    orgId: number;
  }