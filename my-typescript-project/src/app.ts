// Entry point of the application
import { greet } from './types';

const main = () => {
    const message: string = greet('World');
    console.log(message);
};

main();