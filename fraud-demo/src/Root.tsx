import {Composition} from 'remotion';
import {FraudLensDemo, TOTAL_FRAMES} from './Composition';

export const RemotionRoot = () => <Composition
  id="FraudLensProductDemo"
  component={FraudLensDemo}
  durationInFrames={TOTAL_FRAMES}
  fps={30}
  width={1920}
  height={1080}
/>;
