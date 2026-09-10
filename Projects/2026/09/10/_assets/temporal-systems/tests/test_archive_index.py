from dataclasses import replace
import json
from pathlib import Path
import unittest
from archive_index import ArchiveIndex, Sample, Segment, from_json

class ArchiveTests(unittest.TestCase):
    def fixture(self):
        config={'c':{'asset':'init.mp4','range_start':0,'range_length':100}}
        a=Segment('a.m4s',1000,'one','c',0,2_000_000,0,10,
                  (Sample(0,0,True),Sample(10,1,False),Sample(5,2,False)))
        b=replace(a,asset='b.m4s',epoch='reset',start_us=4_000_000,end_us=6_000_000)
        return config,a,b

    def test_gap_reset_selection(self):
        config,a,b=self.fixture()
        index=ArchiveIndex(config,[a,b])
        self.assertEqual(index.resolve(2_000_000)['status'],'gap')
        self.assertEqual(index.resolve(3_999_999)['status'],'gap')
        self.assertEqual(index.resolve(4_100_000)['selected_utc_us'],4_500_000)
        plan=index.resolve(600_000)
        self.assertEqual(plan['selected_pts'],10)
        self.assertEqual(plan['decode_start_dts'],0)
        self.assertEqual(plan['discarded_frame_count'],2)
        self.assertEqual(plan['media'][0]['range_length'],1000)
        self.assertEqual(index.resolve(1_900_000)['status'],'no-frame-before-segment-end')

    def test_invalid_index(self):
        config,a,b=self.fixture()
        for bad in (replace(a,size=-1),replace(a,configuration='unknown'),replace(a,asset='../private'),
                    replace(a,samples=tuple(reversed(a.samples))),
                    replace(a,samples=(Sample(0,0,False),)),replace(a,timescale=0)):
            with self.assertRaises(ValueError):
                ArchiveIndex(config,[bad])
        with self.assertRaises(ValueError):
            ArchiveIndex(config,[a,replace(b,start_us=1_000_000)])
        with self.assertRaises(ValueError):
            ArchiveIndex({'c':{'asset':'init.mp4','range_start':-1,'range_length':100}},[a])

    def test_generated_media_evidence(self):
        root=Path(__file__).resolve().parents[1]/'outputs'/'media'
        for name in ('no-b','b-frames'):
            directory=root/name
            self.assertTrue((directory/'index.json').exists(),'run build_media.py first')
            index=from_json(json.loads((directory/'index.json').read_text()))
            plan=json.loads((directory/'decode-plan.json').read_text())
            self.assertEqual(index.resolve(plan['target_us'])['selected_pts'],plan['observed_first_retained_pts'])
            self.assertEqual(plan['selected_utc_us']-plan['target_us'],50_000)
            self.assertEqual(plan['discarded_frame_count'],8)
            for s in index.segments:
                self.assertEqual((directory/s.asset).stat().st_size,s.size)
            self.assertEqual(bool(plan['reordered_packet_count']),name=='b-frames')
            self.assertGreater((directory/'selected-frame.png').stat().st_size,100)

if __name__=='__main__':
    unittest.main()
