import { Ticket } from "../components/types";

export const initialTickets: Ticket[] = [
  {
    id: 1,
    text: "I tried to pay my bill online but your site kept giving error 500, and the chatbot was no help at all.",
    stage: "uploaded",
  },
  {
    id: 2,
    text: "Just wanted to let you know the delivery was late but it arrived safely. Thanks.",
    stage: "uploaded",
  },
  {
    id: 3,
    text: "Reset my password 3 times, still can't get access. Please fix this ASAP or I'll move to another provider!",
    stage: "uploaded",
  },
];
