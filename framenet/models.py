from django.db import models


class FrameElement(models.Model):
    FE_TYPES = (
        ('CORE', 'CORE'),
        ('NON_CORE', 'NON_CORE'),
    )
    eng_name = models.CharField(max_length=50)
    chi_name = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    abbr = models.CharField(max_length=50)
    fe_type = models.CharField(max_length=10, choices=FE_TYPES)

    def as_dict(self):
        return {
            'eng_name': self.eng_name,
            'chi_name': self.chi_name,
            'description': self.description,
            'abbr': self.abbr,
            'fe_type': self.fe_type
        }

    def __str__(self):
        return '%s/%s' % (self.eng_name, self.chi_name)


class FrameNet(models.Model):
    eng_name = models.CharField(max_length=50, unique=True)
    chi_name = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    frame_elements = models.ManyToManyField(FrameElement)
    fid = models.IntegerField()

    def as_dict(self):
        return {
            'fid': self.fid,
            'eng_name': self.eng_name,
            'chi_name': self.chi_name,
            'description': self.description,
            'frame_elements': [fe.as_dict() for fe in self.frame_elements.all()]
        }

    def __str__(self):
        return '%s/%s' % (self.eng_name, self.chi_name)


class LexUnit(models.Model):
    name = models.CharField(max_length=50)
    pos = models.CharField(max_length=10, blank=True)
    frame = models.ForeignKey(FrameNet)

    class Meta:
        unique_together = ('name', 'pos', 'frame')

    def as_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'pos': self.pos,
            'frame': self.frame.eng_name
        }

    def __str__(self):
        return '%s/%s[%s]' % (self.name, self.pos, self.frame)
